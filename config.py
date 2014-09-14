#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import os

base_dir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'mysql://spt:constintspt@localhost:3306/oj'
SQLALCHEMY_MIGRATE_REPO = os.path.join(base_dir, 'db_repository')

DEBUG = True
CSRF_ENABLED = True
SECRET_KEY = 'rikka0612'

USERID_ERROR = 'User ID can only contain NUMBERs & LETTERs and length must be 3 to 22.'
NICKNAME_ERROR = 'Nick Name must be 6 to 22 characters.'
PASSWORD_ERROR = 'Password can only contain NUMBERs & LETTERs and length must be 6 to 22.'
EQUAL_ERROR = 'Repeat PassWord must be equal to PassWord.'
EXIST_ERROR = 'User ID has been registered!'
CHECK_USERID_ERROR = 'User ID does not exist!'
CHECK_PASSWORD_ERROR = 'Password is not correct!'