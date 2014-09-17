#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from flask.ext.wtf import Form
from wtforms import BooleanField, TextField, PasswordField, TextAreaField
from wtforms.validators import Length
from re import match

class RegisterForm(Form):
    userid = TextField('User ID')
    nickname = TextField('Nick Name')
    password = PasswordField('PassWord')
    rptpassword = PasswordField('Repeat PassWord')

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
    userid = TextField('User ID')
    password = PasswordField('Password')

    def validate_userid(self):
        return match(r'^[a-zA-Z0-9]{4,23}$', self.userid.data)

    def validate_password(self):
        return match(r'^[a-zA-Z0-9]{6,22}$', self.password.data)

    def __repr__(self):
        return str(self.userid.data)

class ProblemForm(Form):
    title = TextField('Title', [Length(max = 299)])
    desc = TextAreaField('Description', [Length(max = 9999)])
    pinput = TextAreaField('Input', [Length(max = 9999)])
    poutput = TextAreaField('Output', [Length(max = 9999)])
    sinput = TextAreaField('Sample Input', [Length(max = 9999)])
    soutput = TextAreaField('Sample Output', [Length(max = 9999)])
    hint = TextAreaField('Hint', [Length(max = 9999)])