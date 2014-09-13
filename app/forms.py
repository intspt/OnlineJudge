#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from flask.ext.wtf import Form
from wtforms import BooleanField, TextField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo
import re

class RegisterForm(Form):
    userID = TextField('userID')
    nickName = TextField('nickName')
    password = PasswordField('password')
    rptpassword = PasswordField('rptpassword')

    def validate_userID(self):
        return re.match(r'^[a-zA-Z0-9]{3,22}$', self.userID.data)

    def validate_nickName(self):
        return 5 < len(self.nickName.data) < 23

    def validate_password(self):
        return re.match(r'^[a-zA-Z0-9]{6,22}$', self.password.data)

    def validate_equal(self):
        return self.password.data == self.rptpassword.data





