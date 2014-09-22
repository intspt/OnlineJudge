#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import os

'''数据库URI'''
SQLALCHEMY_DATABASE_URI = 'mysql://spt:constintspt@localhost:3306/oj'
MAIN_FOLDER = os.getcwd()
'''存放题目数据'''
DATA_FOLDER = os.path.join(MAIN_FOLDER, 'app/data')
'''存放临时文件'''
TMP_FOLDER = os.path.join(MAIN_FOLDER, 'app/tmp')
'''扫描数据库并将Pending状态的提交加入队列的间隔时间'''
WAIT_TIME = 0.5

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

'''每页展示问题的最大数量'''
MAX_PROBLEM_NUM_ONE_PAGE = 100
'''每页展示提交记录的最大数量'''
MAX_SUBMIT_NUM_ONE_PAGE = 20
'''每页展示用户的最大数量'''
USER_NUM_ONE_PAGE = 50

'''管理员账户信息'''
ADMIN_USERID = 'rikka'
ADMIN_NICKNAME = 'rikka'
ADMIN_PASSWORD = '110018'

'''给予python程序的时间与内存限制相比于C/C++的倍数'''
PYTHON_TIME_LIMIT_TIMES = 10
PYTHON_MEMORY_LIMIT_TIMES = 10

JUDGE_RESULT = {
    0: 'Accepted',
    1: 'Presentation Error',
    2: 'Time Limit Exceeded',
    3: 'Memory Limit Exceeded',
    4: 'Wrong Answer',
    5: 'Runtime Error',
    6: 'Output Limit Exceeded',
    7: 'Compile Error',
    8: 'System Error'
}
