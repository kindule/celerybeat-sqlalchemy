#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#=============================================================================
#     FileName: create_all
#         Desc:
#       Author: ge.jin
#        Email: ge.jin@woqutech.com
#     HomePage: wwww.woqutech.com
#      Version: 0.0.1
#   LastChange: 4/27/16 11:09 AM
#      History:
#=============================================================================
'''
from celery import Celery
app = Celery('celerybeat-sqlalchemy')
app.config_from_object('settings')
from model import engine
from model.model import Base

Base.metadata.create_all(engine)


