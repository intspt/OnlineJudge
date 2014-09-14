#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from app import db
from app.models import User

db.drop_all()
db.create_all()