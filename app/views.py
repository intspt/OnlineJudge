#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import os
import time
from functools import wraps
from flask import render_template, request, g, redirect, url_for, flash, abort
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from models import User, Problem, Notification, Submit
from forms import RegisterForm, LoginForm, ProblemForm, NotificationForm, SubmitForm
from config import USERID_ERROR, NICKNAME_ERROR, PASSWORD_ERROR, EQUAL_ERROR, EXIST_ERROR, \
                    CHECK_USERID_ERROR, CHECK_PASSWORD_ERROR, PERMISSION_ERROR, INPUT_ERROR, \
                    UPLOAD_SUCCESS, PAGENUMBER_ERROR, ADD_NOTIFICATION_SUCCESS, \
                    MAX_PROBLEM_NUM_ONE_PAGE, MAX_SUBMIT_NUM_ONE_PAGE

def admin_required(func):
    @wraps(func)
    def check(**args):
        if current_user.is_authenticated() and current_user.is_admin:
            return func(**args)
        else:
            return PERMISSION_ERROR
    return check

def pid_islegal(func):
    @wraps(func)
    def check(**args):
        problem = db.session.query(Problem).filter_by(pid = args['pid']).first()
        if not problem or not problem.visable:
            return render_template('404.html')
        else:
            args['problem'] = problem
            return func(**args)
    return check

def get_now_time():
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

def delete_data(file_name):
    os.system('/'.join(['rm problems', file_name]))

@app.before_request
def before_request():
    g.user = current_user
    tmp = db.session.query(Notification).order_by('notification_mid DESC').first()
    if tmp and tmp.visable:
        g.notification = tmp.content

@lm.user_loader
def load_user(userid):
    return db.session.query(User).get(userid)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/userinfo?userid=<userid>/')
def userinfo(userid):
    return render_template('userinfo.html')

@app.route('/register/', methods = ['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'GET':
        return render_template('register.html', form = form)
    else:
        user = User(userid = form.userid.data, nickname = form.nickname.data, password = form.password.data)
        if not form.validate_userid():
            error = USERID_ERROR
        elif not form.validate_nickName():
            error = NICKNAME_ERROR
        elif not form.validate_password():
            error = PASSWORD_ERROR
        elif not form.validate_equal():
            error = EQUAL_ERROR
        elif db.session.query(User).filter_by(userid = user.userid).first() is not None:
            error = EXIST_ERROR
        else:
            error = None

        if error:
            flash(error)
            return render_template('register.html', form = form)
        else:
            db.session.add(user)
            db.session.commit()
            login_user(user, remember = True)
            return redirect('/')

@app.route('/login/', methods = ['GET', 'POST'])
def login():
    form = LoginForm(next_url = request.args.get('next'))
    if request.method == 'GET':
        return render_template('login.html', form = form)
    else:
        user = db.session.query(User).filter_by(userid = form.userid.data).first()
        if user is None:
            error = CHECK_USERID_ERROR
        elif user.password != form.password.data:
            error = CHECK_PASSWORD_ERROR
        else:
            error = None

        if error:
            flash(error)
            return render_template('login.html', form = form)
        else:
            login_user(user, remember = True)
            return redirect(form.next_url.data or '/')

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(request.referrer or '/')

@app.route('/problemset/')
@app.route('/problemset/<int:pn>/')
def problemset(pn = 1):
    problem_count = db.session.query(Problem).count()
    if (pn - 1) * MAX_PROBLEM_NUM_ONE_PAGE > problem_count:
        return PAGENUMBER_ERROR
    else:
        problem_list = db.session.query(Problem).filter_by(visable = True).order_by('problem_pid').slice((pn - 1) * MAX_PROBLEM_NUM_ONE_PAGE, min(problem_count, pn * MAX_PROBLEM_NUM_ONE_PAGE))
        return render_template('problemset.html', pn = pn, problem_count = problem_count, problem_list = problem_list)

@app.route('/showproblem/<int:pid>/')
@pid_islegal
def show_problem(pid, problem):
    return render_template('showproblem.html', problem = problem)

@app.route('/submit/<int:pid>/', methods = ['GET', 'POST'])
@pid_islegal
@login_required
def submit_problem(pid, problem):
    form = SubmitForm(pid = pid)
    if request.method == 'GET':
        return render_template('submit.html', form = form)
    else:
        submit = Submit(runid = db.session.query(Submit).count() + 1, userid = current_user.userid, \
                    pid = problem.pid, language = form.language.data, src = form.src.data, \
                    submit_time = get_now_time())

        db.session.add(submit)
        db.session.commit()
        return redirect('/status/')

@app.route('/status/')
@app.route('/status/first/<int:first>/')
@app.route('/status/last/<int:last>/')
def status(first = None, last = None):
    submit_list = db.session.query(Submit).order_by('submit_runid').all()
    submit_count = db.session.query(Submit).count()
    if first:
        if first < 0 or first > submit_count:
            abort(404)

        s, t = first - submit_count - 1, max(-(submit_count + 1), first - MAX_SUBMIT_NUM_ONE_PAGE - submit_count + 1)
    elif last:
        if last < 0 or last > submit_count:
            abort(404)

        s, t = min(-1, last + MAX_SUBMIT_NUM_ONE_PAGE - submit_count - 2), max(-(submit_count + 1), last - submit_count - 2)
    else:
        s, t = -1, -min(submit_count, MAX_SUBMIT_NUM_ONE_PAGE) - 1

    return render_template('status.html',  submit_list = submit_list[s: t: -1])

@app.route('/viewcode/<int:runid>')
def viewcode(runid):
    return render_template('viewcode.html', submit = db.session.query(Submit).filter_by(runid = runid).first())

@app.route('/admin/')
@admin_required
def admin():
    return render_template('admin.html')

@app.route('/admin/problemset/')
@app.route('/admin/problemset/<int:pn>')
@admin_required
def admin_problemset(pn = 1):
    problem_count = db.session.query(Problem).count()
    if (pn - 1) * MAX_PROBLEM_NUM_ONE_PAGE > problem_count:
        return PAGENUMBER_ERROR
    else:
        problem_list = db.session.query(Problem).order_by('problem_pid').slice((pn - 1) * MAX_PROBLEM_NUM_ONE_PAGE, min(problem_count, pn * MAX_PROBLEM_NUM_ONE_PAGE))
        return render_template('admin_problemset.html', pn = pn, problem_count = problem_count, problem_list = problem_list)

@app.route('/admin/addproblem/', methods = ['GET', 'POST'])
@admin_required
def admin_add_problem():
    form = ProblemForm()
    if request.method == 'GET':
        return render_template('admin_addproblem.html', form = form)
    else:
        inputfile = request.files['inputfile']
        outputfile = request.files['outputfile']
        problem_count = db.session.query(Problem).count()
        inputfile.save(os.path.join(app.config['UPLOAD_FOLDER'], '.'.join([str(problem_count + 1), 'in'])))
        outputfile.save(os.path.join(app.config['UPLOAD_FOLDER'], '.'.join([str(problem_count + 1), 'out'])))
        problem = Problem(title = form.title.data, desc = form.desc.data, pinput = form.pinput.data, \
            poutput = form.poutput.data, sinput = form.sinput.data, soutput = form.soutput.data, \
            hint = form.hint.data, time_limit = int(form.time_limit.data), memory_limit = int(form.memory_limit.data))

        db.session.add(problem)
        db.session.commit()
        flash(UPLOAD_SUCCESS)
        return redirect('/admin/problemset/')

@app.route('/admin/editproblem/<int:pid>/', methods = ['GET', 'POST'])
@admin_required
def admin_edit_problem(pid):
    form = ProblemForm()
    if request.method == 'GET':
        problem = db.session.query(Problem).filter_by(pid = pid).first()
        form = ProblemForm(title = problem.title, desc = problem.desc, pinput = problem.pinput, \
                poutput = problem.poutput, sinput = problem.sinput, soutput = problem.soutput, \
                hint = problem.hint, time_limit = problem.time_limit, memory_limit = problem.memory_limit)

        return render_template('admin_editproblem.html', form = form, pid = pid)
    else:
        delete_data('.'.join([str(pid + 1), 'in']))
        delete_data('.'.join([str(pid + 1), 'out']))
        inputfile = request.files['inputfile']
        outputfile = request.files['outputfile']
        inputfile.save(os.path.join(app.config['UPLOAD_FOLDER'], '.'.join([str(pid + 1), 'in'])))
        outputfile.save(os.path.join(app.config['UPLOAD_FOLDER'], '.'.join([str(pid + 1), 'out'])))
        db.session.query(Problem).filter_by(pid = pid).update({'title': form.title.data, 'desc': form.desc.data, \
            'pinput': form.pinput.data, 'poutput': form.poutput.data, 'sinput': form.sinput.data, \
            'soutput': form.soutput.data, 'hint': form.hint.data, 'time_limit': form.time_limit.data, \
            'memory_limit': form.memory_limit.data})

        db.session.commit()
        return redirect('/admin/problemset/')

@app.route('/admin/hideproblem/<int:pid>/')
@admin_required
def admin_hide_problem(pid):
    db.session.query(Problem).filter_by(pid = pid).update({"visable": False})
    db.session.commit()
    return redirect(request.referrer)

@app.route('/admin/displayproblem/<int:pid>/')
@admin_required
def admin_display_problem(pid):
    db.session.query(Problem).filter_by(pid = pid).update({"visable": True})
    db.session.commit()
    return redirect(request.referrer)

@app.route('/admin/notification/', methods = ['GET', 'POST'])
@admin_required
def admin_notification():
    form = NotificationForm()
    if request.method == 'GET':
        notification_list = db.session.query(Notification).order_by('notification_mid DESC').all()
        return render_template('admin_notification.html', form = form, notification_list = notification_list)
    else:
        if not form.validate_on_submit():
            flash(INPUT_ERROR)
        else:
            notification = Notification(content = form.content.data, add_time = get_now_time())
            db.session.add(notification)
            db.session.commit()
            flash(ADD_NOTIFICATION_SUCCESS)

        return redirect(request.referrer)