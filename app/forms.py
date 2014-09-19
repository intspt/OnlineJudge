#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from flask.ext.wtf import Form
from wtforms import BooleanField, TextField, PasswordField, TextAreaField, HiddenField
from wtforms.validators import Length
from re import match

class RegisterForm(Form):
    userid = TextField()
    nickname = TextField()
    password = PasswordField()
    rptpassword = PasswordField()

    def validate_userid(self):
        return match(r'^[a-zA-Z0-9]{4,23}$', self.userid.data)

    def validate_nickName(self):
        return 5 < len(self.nickname.data) < 23

    def validate_password(self):
        return match(r'^[a-zA-Z0-9]{6,22}$', self.password.data)

    def validate_equal(self):
        return self.password.data == self.rptpassword.data

    def __repr__(self):
        return str(self.userid.data)

class LoginForm(Form):
    userid = TextField()
    password = PasswordField()
    next_url = HiddenField()

    def validate_userid(self):
        return match(r'^[a-zA-Z0-9]{4,23}$', self.userid.data)

    def validate_password(self):
        return match(r'^[a-zA-Z0-9]{6,22}$', self.password.data)

    def __repr__(self):
        return str(self.userid.data)

class ProblemForm(Form):
    title = TextField()
    desc = TextAreaField()
    pinput = TextAreaField()
    poutput = TextAreaField()
    sinput = TextAreaField()
    soutput = TextAreaField()
    hint = TextAreaField()
    time_limit = TextField()
    memory_limit = TextField()

class NotificationForm(Form):
    message = TextField([Length(max = 80)])

class SubmitForm(Form):
    pass