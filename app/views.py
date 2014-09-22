#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import os
import time
from functools import wraps

from sqlalchemy.sql import or_, and_
from flask import render_template, request, g, redirect, url_for, flash, abort
from flask.ext.login import login_user, logout_user, current_user, login_required

from app import app, db, lm
from models import User, Problem, Notification, Submit
from forms import RegisterForm, LoginForm, ProblemForm, NotificationForm, SubmitForm, SearchProblemForm
from config import USERID_ERROR, NICKNAME_ERROR, PASSWORD_ERROR, EQUAL_ERROR, EXIST_ERROR, \
                    CHECK_USERID_ERROR, CHECK_PASSWORD_ERROR, PERMISSION_ERROR, INPUT_ERROR, \
                    UPLOAD_SUCCESS, PAGENUMBER_ERROR, ADD_NOTIFICATION_SUCCESS, \
                    MAX_PROBLEM_NUM_ONE_PAGE, MAX_SUBMIT_NUM_ONE_PAGE, DATA_FOLDER, USER_NUM_ONE_PAGE

def admin_required(func):
    '''检查是否以管理员身份登陆'''
    @wraps(func)
    def check(**args):
        if current_user.is_authenticated() and current_user.is_admin:
            return func(**args)
        else:
            return PERMISSION_ERROR
    return check

def pid_islegal(func):
    '''检查题目ID是否合法'''
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
    '''获取当前时间'''
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

def delete_data(file_name):
    '''删除旧的题目数据'''
    os.system(' '.join(['rm', os.path.join(DATA_FOLDER, file_name)]))

@app.before_request
def before_request():
    '''每次请求前将当前用户信息以及通知放入g对象中便于模板访问'''
    g.user = current_user
    tmp = db.session.query(Notification).order_by('notification_mid DESC').first()
    if tmp and tmp.visable:
        g.notification = tmp.content

@lm.user_loader
def load_user(userid):
    return db.session.query(User).get(userid)

@app.route('/')
def home():
    '''主页'''
    return render_template('index.html')

@app.route('/faqs/')
def faqs():
    '''FAQ'''
    return render_template('FAQ.html')

@app.route('/userinfo?userid=<userid>/')
def userinfo(userid):
    '''用户信息页面'''
    user = db.session.query(User).filter_by(userid = userid).first()
    solved_problem_list = db.session.query(Submit).filter_by(userid = userid, result = 'Accepted').order_by('submit_pid').distinct('submit_pid').all()
    user_list = db.session.query(User).order_by('user_ac_count DESC, user_submit_count, user_userid').all()
    rank = user_list.index(user) + 1
    return render_template('userinfo.html', user = user, rank = rank, solved_problem_list = solved_problem_list)

@app.route('/register/', methods = ['GET', 'POST'])
def register():
    '''注册页面'''
    form = RegisterForm()
    if request.method == 'GET':
        return render_template('register.html', form = form)
    else:
        user = User(userid = form.userid.data, nickname = form.nickname.data, password = form.password.data)
        if not form.validate_userid():
            error = USERID_ERROR
        elif not form.validate_nickname():
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
    '''登陆页面'''
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
    '''登出页面(重定向到前一页面或主页面)'''
    logout_user()
    return redirect(request.referrer or '/')

@app.route('/problemset/')
@app.route('/problemset/<int:pn>/')
def problemset(pn = 1):
    '''题目列表'''
    form = SearchProblemForm()
    problem_count = db.session.query(Problem).count()
    if (pn - 1) * MAX_PROBLEM_NUM_ONE_PAGE > problem_count:
        return PAGENUMBER_ERROR
    else:
        problem_list = db.session.query(Problem).filter_by(visable = True).order_by('problem_pid').slice((pn - 1) * MAX_PROBLEM_NUM_ONE_PAGE, min(problem_count, pn * MAX_PROBLEM_NUM_ONE_PAGE))
        return render_template('problemset.html', pn = pn, problem_count = problem_count, \
            problem_list = problem_list, form = form)

@app.route('/searchproblem/', methods = ['POST'])
def search_problem():
    '''接受搜索题目请求'''
    form = SearchProblemForm()
    if not form.pid.data:
        return redirect('/problemset/')
    else:
        return redirect(url_for('show_problem', pid = form.pid.data))

@app.route('/showproblem/<int:pid>/')
@pid_islegal
def show_problem(pid, problem):
    '''题目信息页面'''
    return render_template('showproblem.html', problem = problem)

@app.route('/submit/<int:pid>/', methods = ['GET', 'POST'])
@pid_islegal
@login_required
def submit_problem(pid, problem):
    '''提交页面'''
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
    '''提交状态列表'''
    submit_list = db.session.query(Submit).order_by('submit_runid').all()
    submit_count = db.session.query(Submit).count()
    if first:
        if first > submit_count:
            abort(404)
        s, t = first - submit_count - 1, max(-(submit_count + 1), first - MAX_SUBMIT_NUM_ONE_PAGE - submit_count + 1)
    elif last:
        if last > submit_count:
            abort(404)
        s, t = min(-1, last + MAX_SUBMIT_NUM_ONE_PAGE - submit_count - 2), max(-(submit_count + 1), last - submit_count - 2)
    else:
        s, t = -1, -min(submit_count, MAX_SUBMIT_NUM_ONE_PAGE) - 1

    return render_template('status.html', submit_list = submit_list[s: t: -1], first_page = True)

@app.route('/showcompileinfo/<int:runid>/')
def show_compileinfo(runid):
    '''编译报错信息页面'''
    return render_template('ce_error.html', ce_error = db.session.query(Submit).filter_by(runid = runid).first().ce_error)

@app.route('/viewcode/<int:runid>')
def viewcode(runid):
    '''代码查看页面'''
    return render_template('viewcode.html', submit = db.session.query(Submit).filter_by(runid = runid).first())

@app.route('/ranklist/')
@app.route('/ranklist/<int:start>/')
def ranklist(start = 1):
    '''用户排名页面'''
    user_count = db.session.query(User).count()
    if start > user_count:
        abort(404)

    end = min(user_count, start + USER_NUM_ONE_PAGE) + 1
    user_list = db.session.query(User).order_by('user_ac_count DESC, user_submit_count, user_userid')[start - 1: end - 1]
    return render_template('ranklist.html', start = start, end = end, user_list = user_list, user_count = user_count)

@app.route('/admin/')
@admin_required
def admin():
    '''后台主页面'''
    return render_template('admin.html')

@app.route('/admin/problemset/')
@app.route('/admin/problemset/<int:pn>')
@admin_required
def admin_problemset(pn = 1):
    '''后台题目列表页面'''
    problem_count = db.session.query(Problem).count()
    if (pn - 1) * MAX_PROBLEM_NUM_ONE_PAGE > problem_count:
        return PAGENUMBER_ERROR
    else:
        problem_list = db.session.query(Problem).order_by('problem_pid').slice((pn - 1) * MAX_PROBLEM_NUM_ONE_PAGE, min(problem_count, pn * MAX_PROBLEM_NUM_ONE_PAGE))
        return render_template('admin_problemset.html', pn = pn, problem_count = problem_count, problem_list = problem_list)

@app.route('/admin/addproblem/', methods = ['GET', 'POST'])
@admin_required
def admin_add_problem():
    '''后台添加题目页面'''
    form = ProblemForm()
    if request.method == 'GET':
        return render_template('admin_addproblem.html', form = form)
    else:
        inputfile = request.files['inputfile']
        outputfile = request.files['outputfile']
        problem_count = db.session.query(Problem).count()
        inputfile.save(os.path.join(app.config['DATA_FOLDER'], '.'.join([str(problem_count + 1001), 'in'])))
        outputfile.save(os.path.join(app.config['DATA_FOLDER'], '.'.join([str(problem_count + 1001), 'out'])))
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
    '''重新编辑题目页面'''
    form = ProblemForm()
    if request.method == 'GET':
        problem = db.session.query(Problem).filter_by(pid = pid).first()
        form = ProblemForm(title = problem.title, desc = problem.desc, pinput = problem.pinput, \
                poutput = problem.poutput, sinput = problem.sinput, soutput = problem.soutput, \
                hint = problem.hint, time_limit = problem.time_limit, memory_limit = problem.memory_limit)

        return render_template('admin_editproblem.html', form = form, pid = pid)
    else:
        delete_data('.'.join([str(pid), 'in']))
        delete_data('.'.join([str(pid), 'out']))
        inputfile = request.files['inputfile']
        outputfile = request.files['outputfile']
        inputfile.save(os.path.join(app.config['DATA_FOLDER'], '.'.join([str(pid), 'in'])))
        outputfile.save(os.path.join(app.config['DATA_FOLDER'], '.'.join([str(pid), 'out'])))
        db.session.query(Problem).filter_by(pid = pid).update({'title': form.title.data, 'desc': form.desc.data, \
            'pinput': form.pinput.data, 'poutput': form.poutput.data, 'sinput': form.sinput.data, \
            'soutput': form.soutput.data, 'hint': form.hint.data, 'time_limit': form.time_limit.data, \
            'memory_limit': form.memory_limit.data})

        db.session.commit()
        return redirect('/admin/problemset/')

@app.route('/admin/hideproblem/<int:pid>/')
@admin_required
def admin_hide_problem(pid):
    '''隐藏题目'''
    db.session.query(Problem).filter_by(pid = pid).update({"visable": False})
    db.session.commit()
    return redirect(request.referrer)

@app.route('/admin/displayproblem/<int:pid>/')
@admin_required
def admin_display_problem(pid):
    '''显示已隐藏题目'''
    db.session.query(Problem).filter_by(pid = pid).update({"visable": True})
    db.session.commit()
    return redirect(request.referrer)

@app.route('/admin/notification/', methods = ['GET', 'POST'])
@admin_required
def admin_notification():
    '''后台通知页面(添加通知及展示历史通知)'''
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
