#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from app import db

ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
    __tablename__ = 'user'
    userID = db.Column(db.String(22), primary_key = True)
    nickname = db.Column(db.String(22))
    password = db.Column(db.String(120))
    role = db.Column(db.SmallInteger, default = ROLE_USER)

    def __init__(self, userID, nickname, password):
        self.userID = userID
        self.nickname = nickname
        self.password = password

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.userID




