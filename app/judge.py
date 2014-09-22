#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import os
import subprocess
import shlex

import lorun

from app import db
from models import Problem, Submit
from config import DATA_FOLDER, TMP_FOLDER, JUDGE_RESULT, PYTHON_TIME_LIMIT_TIMES, PYTHON_MEMORY_LIMIT_TIMES

def put_task_into_queue(que):
    '''循环扫描数据库,将任务添加到队列'''
    db.session.commit()
    submit_list = db.session.query(Submit).filter_by(result = 'Pending').order_by('submit_runid').all()
    for submit in submit_list:
        task = {
            'runid': submit.runid,
            'pid': submit.pid,
            'language': submit.language,
        }
        que.put(task)

def work(que):
    '''循环扫描队列，获得评判任务并执行'''
    while not que.empty():
        task = que.get()
        runid = task['runid']
        pid = task['pid']
        language = task['language']
        result, rst = judge(runid, pid, language)
        if result == 'Accepted':
            db.session.query(Submit).filter_by(runid = runid).update({'result': result, \
                'time_used': rst['timeused'], 'memory_used': rst['memoryused']})

        else:
            db.session.query(Submit).filter_by(runid = runid).update({'result': result})
        db.session.commit()
        que.task_done()

def get_code(runid, file_name):
    fout = open(os.path.join(TMP_FOLDER, file_name), 'w')
    fout.write(db.session.query(Submit).filter_by(runid = runid).first().src)
    fout.close()

def compile(runid, language):
    '''将程序编译成可执行文件'''
    build_cmd = {
        'C': 'gcc main.c -o main -Wall -lm -O2 -std=c99 --static -DONLINE_JUDGE',
        'C++': 'g++ main.cpp -o main -O2 -Wall -lm --static -DONLINE_JUDGE',
        'Python2.7': 'python2.7 -m py_compile main.py'
    }
    p = subprocess.Popen(build_cmd[language], shell = True, cwd = TMP_FOLDER, \
        stdout = subprocess.PIPE, stderr = subprocess.PIPE)

    out, error =  p.communicate()
    if p.returncode == 0:
        return True
    else:
        db.session.query(Submit).filter_by(runid = runid).update({'ce_error': ''.join([out, error])})
        db.session.commit()
        return False

def judge(runid, pid, language):
    file_name = {
        'C': 'main.c',
        'C++': 'main.cpp',
        'Python2.7': 'main.py'
    }
    get_code(runid, file_name[language])
    input_file = file(os.path.join(DATA_FOLDER, ''.join([str(pid), '.in'])))
    output_file = file(os.path.join(DATA_FOLDER, ''.join([str(pid), '.out'])))
    tmp_file = file(os.path.join(TMP_FOLDER, str(runid)), 'w')
    time_limit = db.session.query(Problem).filter_by(pid = pid).first().time_limit
    memory_limit = db.session.query(Problem).filter_by(pid = pid).first().memory_limit

    if not compile(runid, language):
        return 'Compile Error', None

    if language == 'Python2.7':
        time_limit *= PYTHON_TIME_LIMIT_TIMES
        memory_limit *= PYTHON_MEMORY_LIMIT_TIMES
        cmd = 'python2.7 %s' % (os.path.join(TMP_FOLDER, 'main.pyc'))
        main_exe = shlex.split(cmd)
    else:
        main_exe = [os.path.join(TMP_FOLDER, 'main'), ]

    runcfg = {
        'args': main_exe,
        'fd_in': input_file.fileno(),
        'fd_out': tmp_file.fileno(),
        'timelimit': time_limit,
        'memorylimit': memory_limit
    }
    rst = lorun.run(runcfg)
    tmp_file = file(os.path.join(TMP_FOLDER, str(runid)))
    return JUDGE_RESULT[lorun.check(output_file.fileno(), tmp_file.fileno())], rst