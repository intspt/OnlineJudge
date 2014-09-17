#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import os
from app import db
from app.models import User
from config import ADMIN_USERID, ADMIN_NICKNAME, ADMIN_PASSWORD

os.system('rm -rf app/problems')
os.mkdir('app/problems')
db.drop_all()
db.create_all()
db.session.add(User(userid = ADMIN_USERID, nickname = ADMIN_NICKNAME, password = ADMIN_PASSWORD, is_admin = True))
db.session.commit()