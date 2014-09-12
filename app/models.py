#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from app import db

ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
    userID = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(22), index = True, unique = True)
    password = db.Column(db.String(120), index = True, unique = True)
    role = db.Column(db.SmallInteger, default = ROLE_USER)

    def __init__(self, userID, nickname, password):
        self.userID = userID
        self.nickname = nickname
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.nickname




