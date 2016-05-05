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
pt, _ = PeriodicTask.get_or_create(session_obj=session, name="fsdfafaad", task="task_hello",
                                   crontab=json.dumps({'minute': 1}),
                                   args='[]', kwargs='{}')
# session.add(pt)
# session.flush()


pt, _ = PeriodicTask.get_or_create(session_obj=session, name="dfafaad", task="task_hello",
                                   interval=json.dumps({'every': 30, 'period': 'seconds'}),
                                   args='[]', kwargs='{}')
session.add(pt)
session.flush()
print pt.schedule
