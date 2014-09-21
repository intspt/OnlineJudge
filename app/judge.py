#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from app import db
from models import Submit

def put_task_into_queue(que):
    db.session.commit()
    submit_list = db.session.query(Submit).filter_by(result = 'Pending').order_by('submit_runid').all()
    for submit in submit_list:
        task = {
            'runid': submit.runid,
            'pid': submit.pid,
        }
        que.put(task)

def work(que):
    while not que.empty():
        task = que.get()
        runid = task['runid']
        pid = task['pid']
        # result = judge()
        result = 'Accepted'
        db.session.query(Submit).filter_by(runid = runid).update({'result': result})
        db.session.commit()
        que.task_done()