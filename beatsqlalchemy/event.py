#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#=============================================================================
#     FileName: event
#         Desc:
#       Author: ge.jin
#        Email: ge.jin@woqutech.com
#     HomePage: wwww.woqutech.com
#      Version: 0.0.1
#   LastChange: 4/29/16 4:31 PM
#      History:
#=============================================================================
'''
from sqlalchemy import event

from model import PeriodicTask, PeriodicTasks
from settings import Session


@event.listens_for(Session, "before_flush")
def before_flush(session, flush_context, instances):
    for obj in session.new | session.dirty:
        if isinstance(obj, PeriodicTask):
            PeriodicTasks.changed(session, obj)
