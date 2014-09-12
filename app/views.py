#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from flask import render_template, request, flash, redirect
from app import app
from models import User
from forms import RegisterForm
from config import USERID_ERROR, NICKNAME_ERROR, PASSWORD_ERROR, EQUAL_ERROR

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register/', methods = ['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'GET':
        return render_template('register.html', form = form)
    else:
        if not form.validate_userID():
            print 'id error'
            error = USERID_ERROR
        elif not form.validate_nickName():
            error = NICKNAME_ERROR
        elif not form.validate_password():
            error = PASSWORD_ERROR
        elif not form.validate_equal():
            error = EQUAL_ERROR
        else:
            error = None

        if error:
            return render_template('register.html', form = form, error = error)
        else:
            user = User(form.userID.data, form.nickName.data, form.password.data)
            print user

@app.route('/login/')
def login():
    return render_template('login.html')

@app.route('/problemset/')
def problemset():
    return render_template('base.html')