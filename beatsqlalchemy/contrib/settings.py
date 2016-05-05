#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#=============================================================================
#     FileName: settings
#         Desc:
#       Author: ge.jin
#        Email: ge.jin@woqutech.com
#     HomePage: wwww.woqutech.com
#      Version: 0.0.1
#   LastChange: 4/28/16 9:13 AM
#      History:
#=============================================================================
'''

BEAT_SQLAlchemy_URL = 'mysql+mysqldb://root:letsg0@192.168.99.100:3307/celerybeat?charset=utf8'
CELERYBEAT_SCHEDULER = 'beatsqlalchemy.schedulers.DatabaseScheduler'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
BROKER_URL = 'redis://localhost:6379/0'
