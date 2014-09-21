#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import time
import Queue
from app.judge import put_task_into_queue, work
from app import db
from app.models import Submit

if __name__ == '__main__':
    que = Queue.Queue()
    switch = 0
    while True:
        if switch:
            work(que)
        else:
            put_task_into_queue(que)
            time.sleep(0.5)

        switch ^= 1
