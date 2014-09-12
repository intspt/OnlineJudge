#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from app import app
import flask

@app.route('/')
def home():
    return flask.render_template('index.html')

@app.route('/register/')
def register():
    return flask.render_template('register.html')

@app.route('/login/')
def login():
    return flask.render_template('login.html')

@app.route('/problemset/')
def problemset():
    return flask.render_template('base.html')









































