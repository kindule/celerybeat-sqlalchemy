#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#=============================================================================
#     FileName: addtask
#         Desc:
#       Author: ge.jin
#        Email: ge.jin@woqutech.com
#     HomePage: wwww.woqutech.com
#      Version: 0.0.1
#   LastChange: 5/3/16 9:33 AM
#      History:
#=============================================================================
'''
import json
from celery import Celery, current_app

app = Celery('celerybeat-sqlalchemy')
app.config_from_object('settings')
from model import PeriodicTask, get_session

print current_app.conf.CELERYBEAT_MAX_LOOP_INTERVAL

session = get_session()
# pt = PeriodicTask(name="sdisfsdffaf124asf", task="task_hello",  crontab=cs, interval=iss, args='[]', kwargs='{}')
task_boardcast, _ = PeriodicTask.update_or_create(session_obj=session, name="tasks.boardcast_to",
                                                  task="tasks.boardcast_to",
                                                  defaults=dict(crontab=json.dumps({'minute': '*/1'}),
                                                                args='[1,3,4,"a"]',
                                                                kwargs='{"pp":"workd"}',
                                                                queue="noexist",
                                                                exchange=""))

task_direct, _ = PeriodicTask.update_or_create(session_obj=session, name="tasks.direct_to", task="tasks.direct_to",
                                               defaults=dict(args=[1, 2, 3, 4],
                                                             kwargs={"hello": "world"},
                                                             interval={'every': 30, 'period': 'seconds'}, ))
session.add_all([task_boardcast, task_direct])
session.flush()
