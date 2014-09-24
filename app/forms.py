#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from re import match

from flask.ext.wtf import Form
from wtforms import BooleanField, TextField, PasswordField, TextAreaField, HiddenField, SelectField
from wtforms.validators import Length

class RegisterForm(Form):
    '''注册表单'''
    userid = TextField()
    nickname = TextField()
    password = PasswordField()
    rptpassword = PasswordField()

    def validate_userid(self):
        return match(r'^[a-zA-Z0-9]{4,23}$', self.userid.data)

    def validate_nickname(self):
        return 0 < len(self.nickname.data) < 23

    def validate_password(self):
        return match(r'^[a-zA-Z0-9]{6,22}$', self.password.data)

    def validate_equal(self):
        return self.password.data == self.rptpassword.data

    def __repr__(self):
        return str(self.userid.data)

class LoginForm(Form):
    '''登陆表单'''
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
    '''题目表单'''
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
    '''通知表单'''
    content = TextField([Length(max = 80)])

class SubmitForm(Form):
    '''提交信息表单'''
    pid = TextField()
    language = SelectField(choices = [('C++', 'C++'), ('C', 'C'), ('Python2.7', 'Python2.7')])
    src = TextAreaField()

class SearchProblemForm(Form):
    '''搜索题目表单'''
    pid = TextField()

class SearchSubmitForm(Form):
    '''搜索提交状态表单'''
    pid = TextField()
    userid = TextField()
    language = SelectField(choices = [('All','All'), 
                                        ('C++', 'C++'), \
                                        ('C', 'C'), \
                                        ('Python2.7', 'Python2.7')], \
                                        default = 'All')
    result = SelectField(choices = [('All','All'), \
                                    ('Accepted', 'Accepted'), \
                                    ('Presentation Error', 'Presentation Error'), \
                                    ('Time Limit Exceeded', 'Time Limit Exceeded'), \
                                    ('Memory Limit Exceeded', 'Memory Limit Exceeded'), \
                                    ('Wrong Answer', 'Wrong Answer'), \
                                    ('Runtime Error', 'Runtime Error'), \
                                    ('Output Limit Exceeded', 'Output Limit Exceeded'), \
                                    ('Compile Error', 'Compile Error')], \
                                    default = 'All')
