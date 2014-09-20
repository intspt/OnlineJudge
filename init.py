#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import os
from sqlalchemy import event, DDL
from app import db
from app.models import User, Problem
from config import ADMIN_USERID, ADMIN_NICKNAME, ADMIN_PASSWORD

event.listen(
    Problem.__table__,
    "after_create",
    DDL("ALTER TABLE %(table)s AUTO_INCREMENT = 1001;")
)

os.system('rm -rf app/problems')
os.system('rm -rf app/tmp')
os.mkdir('app/problems')
os.mkdir('app/tmp')
db.drop_all()
db.create_all()
db.session.add(User(userid = ADMIN_USERID, nickname = ADMIN_NICKNAME, password = ADMIN_PASSWORD, is_admin = True))
db.session.commit()