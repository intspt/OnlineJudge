#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from flask import render_template, request, g, redirect, url_for
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from models import User
from forms import RegisterForm, LoginForm
from config import USERID_ERROR, NICKNAME_ERROR, PASSWORD_ERROR, EQUAL_ERROR, EXIST_ERROR, CHECK_USERID_ERROR, CHECK_PASSWORD_ERROR

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_active():
        g.url = url_for('userinfo', userID = g.user.userID)

@lm.user_loader
def load_user(userID):
    return User.query.get(userID)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/<userID>/')
@login_required
def userinfo(userID):
    return render_template('index.html')

@app.route('/register/', methods = ['GET', 'POST'])
def register():
    form = RegisterForm(request.form)    
    if request.method == 'GET':
        return render_template('register.html', form = form)
    else:
        user = User(form.userID.data, form.nickName.data, form.password.data)
        if not form.validate_userID():
            error = USERID_ERROR
        elif not form.validate_nickName():
            error = NICKNAME_ERROR
        elif not form.validate_password():
            error = PASSWORD_ERROR
        elif not form.validate_equal():
            error = EQUAL_ERROR
        elif User.query.filter_by(userID = user.userID).first() is not None:
            error = EXIST_ERROR
        else:
            error = None

        if error:
            return render_template('register.html', form = form, error = error)
        else:
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('userinfo', userID = user.userID))

@app.route('/login/', methods = ['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'GET':
        return render_template('login.html', form = form)
    else:
        user = User.query.filter_by(userID = form.userID.data).first()
        if user is None:
            error = CHECK_USERID_ERROR
        elif user.password != form.password.data:
            error = CHECK_PASSWORD_ERROR
        else:
            error = None

        if error:
            return render_template('login.html', form = form, error = error)
        else:
            login_user(user)
            return redirect('/')

@app.route('/logout/')
def logout():
    logout_user()
    return redirect('/')

@app.route('/problemset/')
def problemset():
    return render_template('base.html')