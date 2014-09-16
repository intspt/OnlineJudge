#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from flask import render_template, request, g, redirect, url_for
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from models import User
from forms import RegisterForm, LoginForm
from config import USERID_ERROR, NICKNAME_ERROR, PASSWORD_ERROR, EQUAL_ERROR, EXIST_ERROR, CHECK_USERID_ERROR, CHECK_PASSWORD_ERROR, PERMISSION_ERROR

def admin_required(func):
    def check():
        if current_user.is_authenticated() and current_user.is_admin:
            return func()
        else:
            return PERMISSION_ERROR
    return check

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.url = url_for('userinfo', userid = g.user.userid)

@lm.user_loader
def load_user(userid):
    return User.query.get(userid)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin/')
@admin_required
def admin():
    return render_template('admin.html')

@app.route('/userinfo?userid=<userid>/')
@login_required
def userinfo(userid):
    return render_template('index.html')

@app.route('/register/', methods = ['GET', 'POST'])
def register():
    form = RegisterForm(request.form)    
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
            return render_template('register.html', form = form, error = error)
        else:
            db.session.add(user)
            db.session.commit()
            login_user(user, remember = True)
            return redirect('/')

@app.route('/login/', methods = ['GET', 'POST'])
def login():
    form = LoginForm(request.form)
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
            return render_template('login.html', form = form, error = error)
        else:
            login_user(user, remember = True)
            return redirect('/')

@app.route('/logout/')
def logout():
    logout_user()
    return redirect('/')

@app.route('/problemset/')
def problemset():
    return render_template('base.html')