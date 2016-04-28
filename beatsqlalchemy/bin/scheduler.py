#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#=============================================================================
#     FileName: celery
#         Desc:
#       Author: ge.jin
#        Email: ge.jin@woqutech.com
#     HomePage: wwww.woqutech.com
#      Version: 0.0.1
#   LastChange: 4/28/16 9:11 AM
#      History:
#=============================================================================
'''
from __future__ import absolute_import

from celery import Celery
app = Celery('celerybeat-sqlalchemy')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
# app.config_from_object('beatsqlalchemy:settings')
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.start()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
    return "Success"
