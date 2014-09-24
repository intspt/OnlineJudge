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
from forms import RegisterForm, LoginForm, ProblemForm, NotificationForm, SubmitForm, SearchProblemForm, SearchSubmitForm
from config import USERID_ERROR, NICKNAME_ERROR, PASSWORD_ERROR, EQUAL_ERROR, EXIST_ERROR, \
                    CHECK_USERID_ERROR, CHECK_PASSWORD_ERROR, PERMISSION_ERROR, INPUT_ERROR, \
                    UPLOAD_SUCCESS, PAGENUMBER_ERROR, ADD_NOTIFICATION_SUCCESS, \
                    MAX_PROBLEM_NUM_ONE_PAGE, MAX_SUBMIT_NUM_ONE_PAGE, DATA_FOLDER, MAX_USER_NUM_ONE_PAGE

def admin_required(func):
    '''检查是否以管理员身份登陆'''
    @wraps(func)
    def check(**args):
        if current_user.is_authenticated() and current_user.is_admin:
            return func(**args)
        else:
            return PERMISSION_ERROR
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
    tmp = Notification.query.order_by('notification.mid DESC').first()
    if tmp and tmp.visable:
        g.notification = tmp.content

@lm.user_loader
def load_user(userid):
    return User.query.get(userid)

@app.route('/')
def home():
    '''主页'''
    return render_template('index.html')

@app.route('/faqs')
def faqs():
    '''FAQ'''
    return render_template('FAQ.html')

@app.route('/userinfo')
def userinfo():
    '''用户信息页面'''
    userid = request.args.get('userid')
    user = User.query.filter_by(userid = userid).first()
    solved_problem_list = db.session.query(Submit.pid).distinct().filter_by(userid = userid, result = 'Accepted').order_by('submit.pid').all()
    user_list = User.query.order_by('user.ac_count DESC, user.submit_count, user.userid').all()
    rank = user_list.index(user) + 1
    return render_template('userinfo.html', user = user, rank = rank, solved_problem_list = solved_problem_list)

@app.route('/register', methods = ['GET', 'POST'])
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
        elif User.query.filter_by(userid = user.userid).first() is not None:
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

@app.route('/login', methods = ['GET', 'POST'])
def login():
    '''登陆页面'''
    form = LoginForm(next_url = request.args.get('next'))
    if request.method == 'GET':
        return render_template('login.html', form = form)
    else:
        user = User.query.filter_by(userid = form.userid.data).first()
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

@app.route('/logout')
@login_required
def logout():
    '''登出页面(重定向到前一页面或主页面)'''
    logout_user()
    return redirect(request.referrer or '/')

@app.route('/problemset')
def problemset():
    '''题目列表'''
    pn = request.args.get('pn')
    pid = request.args.get('pid')
    form = SearchProblemForm()
    if not pn:
        pn = 1
    else:
        pn = int(pn)
    if pid:
        problem_list = Problem.query.filter_by(pid = pid).filter_by(visable = True).paginate(pn, MAX_PROBLEM_NUM_ONE_PAGE)
    else:
        problem_list = Problem.query.filter_by(visable = True).order_by('problem.pid').paginate(pn, MAX_PROBLEM_NUM_ONE_PAGE)
    return render_template('problemset.html', pn = pn, problem_list = problem_list, form = form)

@app.route('/showproblem')
def show_problem():
    '''题目信息页面'''
    pid = request.args.get('pid')
    problem = Problem.query.filter_by(pid = pid).first()
    return render_template('showproblem.html', problem = problem)

@app.route('/submit', methods = ['GET', 'POST'])
@login_required
def submit_problem():
    '''提交页面'''
    pid = request.args.get('pid')
    form = SubmitForm(pid = pid)
    if request.method == 'GET':
        return render_template('submit.html', form = form)
    else:
        submit = Submit(runid = Submit.query.count() + 1, userid = current_user.userid, \
            pid = form.pid.data, language = form.language.data, src = form.src.data, \
            submit_time = get_now_time())

        db.session.add(submit)
        db.session.commit()
        return redirect('/status')

@app.route('/problemstatus')
def problemstatus():
    '''题目状态列表'''
    pn = request.args.get('pn')
    pid = request.args.get('pid')
    if not pn:
        pn = 1
    else:
        pn = int(pn)

    solution_list = Submit.query.filter_by(pid = pid, result = 'Accepted').order_by('submit.time_used, submit.memory_used').group_by('submit.userid').paginate(pn, MAX_SUBMIT_NUM_ONE_PAGE)
    return render_template('problemstatus.html', pid = pid, pn = pn, solution_list = solution_list, MAX_SUBMIT_NUM_ONE_PAGE = MAX_SUBMIT_NUM_ONE_PAGE)

@app.route('/status')
def status():
    '''提交状态列表'''
    top = request.args.get('top')
    bottom = request.args.get('bottom')
    pid = request.args.get('pid')
    userid = request.args.get('userid')
    result = request.args.get('result')
    language = request.args.get('language')
    form = SearchSubmitForm(request.args)

    subq = Submit.query
    if bottom:
        subq = subq.filter(Submit.runid > bottom)
    elif top:
        subq = subq.filter(Submit.runid < top)

    subq = subq.order_by('submit.runid DESC')
    if pid:
        subq = subq.filter_by(pid = pid)
    if userid:
        subq = subq.filter_by(userid = userid)
    if result and result != 'All':
        print result
        subq = subq.filter_by(result = result)
    if language and language != 'All':
        subq = subq.filter_by(language = language)

    submit_list = subq.all()
    return render_template('status.html', form = form, submit_list = submit_list, pid = pid, \
                userid = userid, result = result, language = language)

@app.route('/showcompileinfo')
def show_compileinfo():
    '''编译报错信息页面'''
    runid = request.args.get('runid')
    return render_template('ce_error.html', ce_error = Submit.query.filter_by(runid = runid).first().ce_error)

@app.route('/viewcode')
def viewcode():
    '''代码查看页面'''
    runid = request.args.get('runid')
    return render_template('viewcode.html', submit = Submit.query.filter_by(runid = runid).first())

@app.route('/ranklist')
def ranklist():
    '''用户排名页面'''
    pn = request.args.get('pn')
    if not pn:
        pn = 1
    else:
        pn = int(pn)
    user_list = User.query.order_by('user.ac_count DESC, user.submit_count, user.userid').paginate(pn, MAX_USER_NUM_ONE_PAGE)
    return render_template('ranklist.html', user_list = user_list, pn = pn, MAX_USER_NUM_ONE_PAGE = MAX_USER_NUM_ONE_PAGE)

@app.route('/admin')
@admin_required
def admin():
    '''后台主页面'''
    return render_template('admin.html')

@app.route('/admin/problemset')
@admin_required
def admin_problemset():
    '''后台题目列表页面'''
    pn = request.args.get('pn')
    if not pn:
        pn = 1
    else:
        pn = int(pn)
    problem_list = problem_list = Problem.query.order_by('problem.pid').paginate(pn, MAX_PROBLEM_NUM_ONE_PAGE)
    return render_template('admin_problemset.html', pn = pn, problem_list = problem_list)

@app.route('/admin/addproblem', methods = ['GET', 'POST'])
@admin_required
def admin_add_problem():
    '''后台添加题目页面'''
    form = ProblemForm()
    if request.method == 'GET':
        return render_template('admin_addproblem.html', form = form)
    else:
        inputfile = request.files['inputfile']
        outputfile = request.files['outputfile']
        problem_count = Problem.query.count()
        inputfile.save(os.path.join(app.config['DATA_FOLDER'], '.'.join([str(problem_count + 1001), 'in'])))
        outputfile.save(os.path.join(app.config['DATA_FOLDER'], '.'.join([str(problem_count + 1001), 'out'])))
        problem = Problem(title = form.title.data, desc = form.desc.data, pinput = form.pinput.data, \
            poutput = form.poutput.data, sinput = form.sinput.data, soutput = form.soutput.data, \
            hint = form.hint.data, time_limit = int(form.time_limit.data), memory_limit = int(form.memory_limit.data))

        db.session.add(problem)
        db.session.commit()
        flash(UPLOAD_SUCCESS)
        return redirect('/admin/problemset')

@app.route('/admin/editproblem', methods = ['GET', 'POST'])
@admin_required
def admin_edit_problem():
    '''重新编辑题目页面'''
    pid = request.args.get('pid')
    form = ProblemForm()
    if request.method == 'GET':
        problem = Problem.query.filter_by(pid = pid).first()
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
        Problem.query.filter_by(pid = pid).update({'title': form.title.data, 'desc': form.desc.data, \
            'pinput': form.pinput.data, 'poutput': form.poutput.data, 'sinput': form.sinput.data, \
            'soutput': form.soutput.data, 'hint': form.hint.data, 'time_limit': form.time_limit.data, \
            'memory_limit': form.memory_limit.data})

        db.session.commit()
        return redirect('/admin/problemset')

@app.route('/admin/hideproblem')
@admin_required
def admin_hide_problem():
    '''隐藏题目'''
    pid = request.args.get('pid')
    Problem.query.filter_by(pid = pid).update({"visable": False})
    db.session.commit()
    return redirect(request.referrer)

@app.route('/admin/displayproblem')
@admin_required
def admin_display_problem():
    '''显示已隐藏题目'''
    pid = request.args.get('pid')
    Problem.query.filter_by(pid = pid).update({"visable": True})
    db.session.commit()
    return redirect(request.referrer)

@app.route('/admin/notification/', methods = ['GET', 'POST'])
@admin_required
def admin_notification():
    '''后台通知页面(添加通知及展示历史通知)'''
    form = NotificationForm()
    if request.method == 'GET':
        notification_list = Notification.query.order_by('notification.mid DESC').all()
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

@app.route('/discuss')
def discuss():
    return render_template('discuss.html')
