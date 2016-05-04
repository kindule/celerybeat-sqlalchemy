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
from sqlalchemy.orm import relationship
from .base import Base
from celery import schedules
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Boolean
from sqlalchemy_utils.types.choice import ChoiceType


class ValidationError(Exception):
    pass


class IntervalSchedule(Base):
    __tablename__ = "interval_schedule"
    PERIOD_CHOICES = (('days', 'Days'),
                      ('hours', 'Hours'),
                      ('minutes', 'Minutes'),
                      ('seconds', 'Seconds'),
                      ('microseconds', 'Microseconds'))

    every = Column(Integer, nullable=False)
    period = Column(ChoiceType(PERIOD_CHOICES))
    periodic_tasks = relationship('PeriodicTask')

    @property
    def schedule(self):
        return schedules.schedule(datetime.timedelta(**{self.period.code: self.every}))

    @classmethod
    def from_schedule(cls, session, schedule, period='seconds'):
        every = max(schedule.run_every.total_seconds(), 0)
        obj = cls.filter_by(session, every=every, period=period).first()
        if obj is None:
            return cls(every=every, period=period)
        else:
            return obj

    def __str__(self):
        if self.every == 1:
            return _('every {0.period_singular}').format(self)
        return _('every {0.every} {0.period}').format(self)

    @property
    def period_singular(self):
        return self.period[:-1]


class CrontabSchedule(Base):
    """
    Task result/status.
    """
    __tablename__ = "crontab_schedule"
    minute = Column(String(length=120), default="*")
    hour = Column(String(length=120), default="*")
    day_of_week = Column(String(length=120), default="*")
    day_of_month = Column(String(length=120), default="*")
    month_of_year = Column(String(length=120), default="*")
    periodic_tasks = relationship('PeriodicTask')

    def __str__(self):
        rfield = lambda f: f and str(f).replace(' ', '') or '*'
        return '{0} {1} {2} {3} {4} (m/h/d/dM/MY)'.format(
            rfield(self.minute), rfield(self.hour), rfield(self.day_of_week),
            rfield(self.day_of_month), rfield(self.month_of_year),
        )

    @property
    def schedule(self):
        return schedules.crontab(minute=self.minute,
                                 hour=self.hour,
                                 day_of_week=self.day_of_week,
                                 day_of_month=self.day_of_month,
                                 month_of_year=self.month_of_year)

    @classmethod
    def from_schedule(cls, session, schedule):
        spec = {'minute': schedule._orig_minute,
                'hour': schedule._orig_hour,
                'day_of_week': schedule._orig_day_of_week,
                'day_of_month': schedule._orig_day_of_month,
                'month_of_year': schedule._orig_month_of_year}
        obj = cls.filter_by(session, **spec).first()
        if obj is None:
            return cls(**spec)
        else:
            return obj


class PeriodicTasks(Base):
    __tablename__ = "periodic_tasks"

    ident = Column(Integer, default=1, primary_key=True)
    last_update = Column(DateTime, default=datetime.datetime.utcnow)

    @classmethod
    def changed(cls, session, instance):
        if not instance.no_changes:
            obj, _ = cls.update_or_create(session, defaults={'last_update': datetime.datetime.now()}, ident=1)
            session.add(obj)

    @classmethod
    def last_change(cls, session):
        obj = cls.filter_by(session, ident=1).first()
        return obj.last_update if obj else None


class PeriodicTask(Base):
    __tablename__ = "periodic_task"

    name = Column(String(length=120), unique=True)
    task = Column(String(length=120))
    crontab_id = Column(Integer, ForeignKey('crontab_schedule.id'))
    crontab = relationship("CrontabSchedule", back_populates="periodic_tasks")
    interval_id = Column(Integer, ForeignKey('interval_schedule.id'))
    interval = relationship("IntervalSchedule", back_populates="periodic_tasks")
    args = Column(String(length=120))
    kwargs = Column(String(length=120))
    last_run_at = Column(DateTime, default=datetime.datetime.utcnow)
    total_run_count = Column(Integer, default=0)
    enabled = Column(Boolean, default=True)
    no_changes = False

    def __str__(self):
        fmt = '{0.name}: {0.crontab}'
        return fmt.format(self)

    @property
    def schedule(self):
        if self.crontab:
            return self.crontab.schedule
        if self.interval:
            return self.interval.schedule
