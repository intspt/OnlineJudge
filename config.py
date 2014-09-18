#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import os

SQLALCHEMY_DATABASE_URI = 'mysql://spt:constintspt@localhost:3306/oj'
UPLOAD_FOLDER = 'app/problems'

DEBUG = True
CSRF_ENABLED = True
SECRET_KEY = 'dark flame master'

USERID_ERROR = 'User ID can only contain NUMBERs & LETTERs and length must be 3 to 22!'
NICKNAME_ERROR = 'Nick Name must be 6 to 22 characters!'
PASSWORD_ERROR = 'Password can only contain NUMBERs & LETTERs and length must be 6 to 22!'
EQUAL_ERROR = 'Repeat PassWord must be equal to PassWord!'
EXIST_ERROR = 'User ID has been registered!'
CHECK_USERID_ERROR = 'User ID does not exist!'
CHECK_PASSWORD_ERROR = 'Password is not correct!'
PERMISSION_ERROR = 'You are not authorized to access this page!'
INPUT_ERROR = 'Input Limit Exceeded!'
PAGENUMBER_ERROR = 'Illegal page number!'
UPLOAD_SUCCESS = 'Uploaded successfully'
ADD_NOTIFICATION_SUCCESS = 'Notification has been added!'

ADMIN_USERID = 'rikka'
ADMIN_NICKNAME = 'rikka'
ADMIN_PASSWORD = '110018'