#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from flask.ext.wtf import Form
from wtforms import BooleanField, TextField, PasswordField, TextAreaField
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

    def validate_userid(self):
        return match(r'^[a-zA-Z0-9]{4,23}$', self.userid.data)

    def validate_password(self):
        return match(r'^[a-zA-Z0-9]{6,22}$', self.password.data)

    def __repr__(self):
        return str(self.userid.data)

class ProblemForm(Form):
    title = TextField([Length(max = 299)])
    desc = TextAreaField([Length(max = 9999)])
    pinput = TextAreaField([Length(max = 9999)])
    poutput = TextAreaField([Length(max = 9999)])
    sinput = TextAreaField([Length(max = 9999)])
    soutput = TextAreaField([Length(max = 9999)])
    hint = TextAreaField([Length(max = 9999)])

class NotificationForm(Form):
    message = TextField([Length(max = 80)])

class SubmitForm(Form):
    pass