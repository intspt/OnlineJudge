#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from app import db

class User(db.Model):
    userid = db.Column(db.String(22), primary_key = True)
    nickname = db.Column(db.String(22))
    password = db.Column(db.String(120))
    is_admin = db.Column(db.Boolean)

    def __init__(self, userid, nickname, password, is_admin = False):
        self.userid = userid
        self.nickname = nickname
        self.password = password
        self.is_admin = is_admin

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.userid

class Problem(db.Model):
    pid = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(299))
    desc = db.Column(db.String(9999))
    pinput = db.Column(db.String(9999))
    poutput = db.Column(db.String(9999))
    sinput = db.Column(db.String(9999))
    soutput = db.Column(db.String(9999))
    hint = db.Column(db.String(9999))

    def __init__(self, pid, title, desc, pinput, poutput, sinput, soutput, hint = None):
        self.pid = pid
        self.title = title
        self.desc = desc
        self.pinput = pinput
        self.poutput = poutput
        self.sinput = sinput
        self.soutput = soutput
        self.hint = hint