#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import os
from functools import wraps
from flask import render_template, request, g, redirect, url_for, flash
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from models import User, Problem, Notification
from forms import RegisterForm, LoginForm, ProblemForm, NotificationForm
from config import USERID_ERROR, NICKNAME_ERROR, PASSWORD_ERROR, EQUAL_ERROR, EXIST_ERROR, \
                    CHECK_USERID_ERROR, CHECK_PASSWORD_ERROR, PERMISSION_ERROR, INPUT_ERROR, \
                    UPLOAD_SUCCESS, PAGENUMBER_ERROR, ADD_NOTIFICATION_SUCCESS

def admin_required(func):
    @wraps(func)
    def check():
        if current_user.is_authenticated() and current_user.is_admin:
            return func()
        else:
            return PERMISSION_ERROR
    return check

@app.before_request
def before_request():
    g.user = current_user
    tmp = Notification.query.order_by('notification_mid DESC').all()
    if tmp and tmp[0].visable:
        g.message = tmp[0].message

@lm.user_loader
def load_user(userid):
    return User.query.get(userid)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/userinfo?userid=<userid>/')
@login_required
def userinfo(userid):
    return render_template('index.html')

@app.route('/register/', methods = ['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'GET':
        return render_template('register.html', form = form)
    else:
        user = User(form.userid.data, form.nickName.data, form.password.data)
        if not form.validate_userid():
            error = USERID_ERROR
        elif not form.validate_nickName():
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

@app.route('/login/', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
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
            return redirect('/')

@app.route('/logout/')
def logout():
    logout_user()
    return redirect('/')

@app.route('/problemset/')
@app.route('/problemset/<int:pn>/')
def problemset(pn = 1):
    problem_count = Problem.query.count()
    if (pn - 1) * 100 > problem_count:
        return PAGENUMBER_ERROR
    else:
        problem_list = Problem.query.order_by('problem_pid').slice((pn - 1) * 100, min(problem_count, pn * 100))
        return render_template('problemset.html', pn = pn, problem_count = problem_count, problem_list = problem_list)

@app.route('/showproblem/<int:pid>/')
def show_problem(pid):
    return render_template('showproblem.html')

@app.route('/admin/')
@admin_required
def admin():
    return render_template('admin.html')

@app.route('/admin/problemset/')
@admin_required
def admin_problemset():
    return render_template('admin_problemset.html')

@app.route('/admin/problemset/addproblem/', methods = ['GET', 'POST'])
@admin_required
def admin_addproblem():
    form = ProblemForm(request.form)
    if request.method == 'GET':
        return render_template('admin_addproblem.html', form = form)
    else:
        inputfile = request.files['inputfile']
        outputfile = request.files['outputfile']
        problem_count = Problem.query.count()
        inputfile.save(os.path.join(app.config['UPLOAD_FOLDER'], '.'.join([str(problem_count + 1), 'in'])))
        outputfile.save(os.path.join(app.config['UPLOAD_FOLDER'], '.'.join([str(problem_count + 1), 'out'])))
        problem = Problem(form.title.data, form.desc.data, form.pinput.data, \
            form.poutput.data, form.sinput.data, form.soutput.data, form.hint.data)

        db.session.add(problem)
        db.session.commit()
        flash(UPLOAD_SUCCESS)
        return redirect('/admin/problemset/')

@app.route('/admin/notification/', methods = ['GET', 'POST'])
@admin_required
def admin_notification():
    form = NotificationForm()
    if request.method == 'GET':
        return render_template('admin_notification.html', form = form)
    else:
        if not form.validate_on_submit():
            flash(INPUT_ERROR)
        else:
            notification = Notification(form.message.data)
            db.session.add(notification)
            db.session.commit()
            flash(ADD_NOTIFICATION_SUCCESS)

        return redirect('/admin/notification/')