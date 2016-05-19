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

    class CrontabSchedule(object):

        def __init__(self, minute="*", hour="*", day_of_week="*", day_of_month="*", month_of_year="*"):
            self.schedule = celery.schedules.crontab(minute, hour, day_of_week, day_of_month, month_of_year)
            self.minute = minute
            self.hour = hour
            self.day_of_week = day_of_week
            self.day_of_month = day_of_month
            self.month_of_year = month_of_year

        def dumps(self):
            return json.dumps({'minute': self.minute,
                               'hour': self.hour,
                               'day_of_week': self.day_of_week,
                               'day_of_month': self.day_of_month,
                               'month_of_year': self.month_of_year})

        @classmethod
        def from_schedule(cls, schedule):
            spec = {'minute': schedule._orig_minute,
                    'hour': schedule._orig_hour,
                    'day_of_week': schedule._orig_day_of_week,
                    'day_of_month': schedule._orig_day_of_month,
                    'month_of_year': schedule._orig_month_of_year}
            return cls(**spec)

    class IntervalSchedule(object):
        def __init__(self, every, period='seconds'):
            self.schedule = celery.schedules.schedule(datetime.timedelta(**{period: every}))
            self.every = every
            self.period = period

        def dumps(self):
            return json.dumps({"every": self.every,
                               "period": self.period})

        @classmethod
        def from_schedule(cls, schedule, period='seconds'):
            every = max(schedule.run_every.total_seconds(), 0)
            return cls(every=every, period=period)

    @validates('crontab', 'interval')
    def schedule_validation(self, schedule_type, schedule):
        schedules = {'crontab': self.CrontabSchedule,
                     'interval': self.IntervalSchedule}
        if schedule is not None:
            if isinstance(schedule, basestring):
                return schedules[schedule_type](**json.loads(schedule)).dumps()
            elif isinstance(schedule, dict):
                return schedules[schedule_type](**schedule).dumps()
            elif isinstance(schedule, celery.schedules.schedule):
                return schedules[schedule_type].from_schedule(schedule).dumps()

    @validates('args', 'kwargs')
    def param_validation(self, key, value):
        if value is not None:
            if isinstance(value, basestring):
                return json.dumps(json.loads(value))
            elif isinstance(value, (dict, list)):
                return json.dumps(value)

    def __str__(self):
        fmt = '{0.name}: {0.crontab}'
        return fmt.format(self)

    @property
    def schedule(self):
        if self.crontab:
            return self.CrontabSchedule(**json.loads(self.crontab)).schedule
        if self.interval:
            return self.IntervalSchedule(**json.loads(self.interval)).schedule
