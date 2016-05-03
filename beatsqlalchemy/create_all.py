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
from .settings import engine
from model.model import Base

Base.metadata.create_all(engine)

# tables = (CrontabSchedule, PeriodicTasks)
#
#
# for table in tables:
#     table.__table__.create(engine)
