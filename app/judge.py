#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import os
import subprocess
import shlex

import lorun

from app import db
from models import Problem, Submit, User
from config import DATA_FOLDER, TMP_FOLDER, JUDGE_RESULT, PYTHON_TIME_LIMIT_TIMES, PYTHON_MEMORY_LIMIT_TIMES

def put_task_into_queue(que):
    '''循环扫描数据库,将任务添加到队列'''
    db.session.commit()
    submit_list = Submit.query.filter_by(result = 'Pending').order_by('submit_runid').all()
    for submit in submit_list:
        task = {
            'runid': submit.runid,
            'pid': submit.pid,
            'language': submit.language,
            'userid': submit.userid
        }
        que.put(task)

def work(que):
    '''循环扫描队列，获得评判任务并执行'''
    while not que.empty():
        task = que.get()
        runid = task['runid']
        pid = task['pid']
        userid = task['userid']
        language = task['language']
        Submit.query.filter_by(runid = runid).update({'result': 'Runing'})
        result, rst = judge(runid, pid, language)
        problem = Problem.query.filter_by(pid = pid).first()
        user = User.query.filter_by(userid = userid).first()
        if result == 'Accepted':
            if not Submit.query.filter_by(pid = pid, userid = userid, result = 'Accepted').all():
                user.ac_count += 1
            Submit.query.filter_by(runid = runid).update({'result': result, \
                'time_used': rst['timeused'], 'memory_used': rst['memoryused']})
            problem.ac_count += 1
        else:
            Submit.query.filter_by(runid = runid).update({'result': result})

        problem.submit_count += 1
        user.submit_count += 1
        db.session.commit()
        que.task_done()
        rm_tmp_file(runid)

def get_code(runid, file_name):
    '''获取对应runid的源代码'''
    fout = open(os.path.join(TMP_FOLDER, file_name), 'w')
    fout.write(Submit.query.filter_by(runid = runid).first().src)
    fout.close()

def rm_tmp_file(runid):
    '''删除产生的临时文件'''
    os.system(' '.join(['rm', os.path.join(TMP_FOLDER, str(runid))]))

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
        Submit.query.filter_by(runid = runid).update({'ce_error': ''.join([out, error])})
        db.session.commit()
        return False

def judge(runid, pid, language):
    '''评测题目'''
    file_name = {
        'C': 'main.c',
        'C++': 'main.cpp',
        'Python2.7': 'main.py'
    }
    get_code(runid, file_name[language])
    input_file = file(os.path.join(DATA_FOLDER, ''.join([str(pid), '.in'])))
    output_file = file(os.path.join(DATA_FOLDER, ''.join([str(pid), '.out'])))
    tmp_file = file(os.path.join(TMP_FOLDER, str(runid)), 'w')
    time_limit = Problem.query.filter_by(pid = pid).first().time_limit
    memory_limit = Problem.query.filter_by(pid = pid).first().memory_limit

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
