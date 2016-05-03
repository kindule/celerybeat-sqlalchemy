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
from settings import Session
from model import CrontabSchedule
from model import PeriodicTask


session = Session()

cs = CrontabSchedule(minute='*/5')
session.add(cs)
session.commit()

pt = PeriodicTask(name="jinge", task="task_hello", crontab=cs, args='[]', kwargs='{}')
session.add(pt)
session.commit()
