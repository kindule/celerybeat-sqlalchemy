#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#=============================================================================
#     FileName: model
#         Desc:
#       Author: ge.jin
#        Email: ge.jin@woqutech.com
#     HomePage: wwww.woqutech.com
#      Version: 0.0.1
#   LastChange: 4/13/16 3:38 PM
#      History:
#=============================================================================
'''
import datetime
import json
import celery.schedules

from sqlalchemy import Column, String, DateTime, Integer, Boolean
from sqlalchemy.orm import validates

from .base import Base


class ValidationError(Exception):
    pass


class PeriodicTask(Base):
    __tablename__ = "periodic_task"

    name = Column(String(length=120), unique=True)
    task = Column(String(length=120))
    crontab = Column(String(length=120))
    interval = Column(String(length=120))
    args = Column(String(length=120))
    kwargs = Column(String(length=120))
    last_run_at = Column(DateTime, default=datetime.datetime.utcnow)
    total_run_count = Column(Integer, default=0)
    enabled = Column(Boolean, default=True)
    run_immediately = Column(Boolean, default=True)
    # options
    queue = Column(String(length=120))
    exchange = Column(String(length=120))
    routing_key = Column(String(length=120))
    soft_time_limit = Column(Integer, default=0)
    expires = Column(DateTime)

    @validates('crontab', 'interval')
    def interval_validation(self, schedule_type, schedule):
        keymap = {'crontab': {'minute': '*',
                              'hour': '*',
                              'day_of_week': '*',
                              'day_of_month': '*',
                              'month_of_year': '*'},
                  'interval': {'period': 'seconds', 'every': 300}}
        if schedule is not None:
            orig_field = json.loads(schedule)
            if set(orig_field.keys()).issubset(keymap[schedule_type].keys()):
                keymap[schedule_type].update(json.loads(schedule))
                return json.dumps(keymap[schedule_type])
            else:
                raise Exception("schedule_type {} invalid value {}".format(schedule_type, schedule))

    def __str__(self):
        fmt = '{0.name}: {0.crontab}'
        return fmt.format(self)

    @property
    def schedule(self):
        if self.crontab:
            return celery.schedules.crontab(**json.loads(self.crontab))
        if self.interval:
            interval = json.loads(self.interval)
            return celery.schedules.schedule(datetime.timedelta(**{interval["period"]: interval["every"]}))
