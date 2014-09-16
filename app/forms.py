#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from flask.ext.wtf import Form
from wtforms import BooleanField, TextField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo
from re import match

class RegisterForm(Form):
    userid = TextField('User ID')
    nickName = TextField('Nick Name')
    password = PasswordField('PassWord')
    rptpassword = PasswordField('Repeat PassWord')

    def validate_userid(self):
        return match(r'^[a-zA-Z0-9]{4,23}$', self.userid.data)

    def validate_nickName(self):
        return 5 < len(self.nickName.data) < 23

    def validate_password(self):
        return match(r'^[a-zA-Z0-9]{6,22}$', self.password.data)

    def validate_equal(self):
        return self.password.data == self.rptpassword.data

class LoginForm(Form):
    userid = TextField('User ID')
    password = PasswordField('Password')

    def validate_userid(self):
        return match(r'^[a-zA-Z0-9]{4,23}$', self.userid.data)

    def validate_password(self):
        return match(r'^[a-zA-Z0-9]{6,22}$', self.password.data)

