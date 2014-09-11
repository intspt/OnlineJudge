#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from app import app
import flask

@app.route('/')
def root():
    return flask.render_template('index.html')

@app.route('/login/')
def login():
    return flask.render_template('login.html')



























