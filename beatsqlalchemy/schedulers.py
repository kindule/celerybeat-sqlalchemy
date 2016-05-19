#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#=============================================================================
#     FileName: schedulers
#         Desc:
#       Author: ge.jin
#        Email: ge.jin@woqutech.com
#     HomePage: wwww.woqutech.com
#      Version: 0.0.1
#   LastChange: 4/13/16 3:38 PM
#      History:
#=============================================================================
'''
import json
from multiprocessing.util import Finalize
import datetime

import sqlalchemy
from celery import current_app
from celery import schedules
from celery.beat import ScheduleEntry, Scheduler
from celery.utils.encoding import safe_str
from celery.utils.log import get_logger
from celery.utils.timeutils import is_naive
from .db import PeriodicTask, get_session

DEFAULT_MAX_INTERVAL = 5

ADD_ENTRY_ERROR = """\
Couldn't add entry %r to database schedule: %r. Contents: %r
"""

logger = get_logger(__name__)
debug, info, error = logger.debug, logger.info, logger.error


class ModelEntry(ScheduleEntry):
    model_schedules = ((schedules.crontab, PeriodicTask.CrontabSchedule, 'crontab'),
                       (schedules.schedule, PeriodicTask.IntervalSchedule, 'interval'))
    save_fields = ['last_run_at', 'total_run_count', 'run_immediately']

    def __init__(self, model):
        self.app = current_app
        self.name = model.name
        self.task = model.task
        self.schedule = model.schedule
        self.args = json.loads(model.args or '[]')
        self.kwargs = json.loads(model.kwargs or '{}')
        self.total_run_count = model.total_run_count
        self.model = model
        self.options = {
            'queue': self.model.queue,
            'exchange': self.model.exchange,
            'routing_key': self.model.routing_key,
            'expires': self.model.expires,
            'soft_time_limit': self.model.soft_time_limit
        }
        if not model.last_run_at:
            model.last_run_at = self._default_now()
        orig = self.last_run_at = model.last_run_at
        if not is_naive(self.last_run_at):
            self.last_run_at = self.last_run_at.replace(tzinfo=None)
        assert orig.hour == self.last_run_at.hour  # timezone sanity

    def _disable(self, model, session):
        model.no_changes = True
        model.enabled = False
        session.add(model)

    def is_due(self):
        if not self.model.enabled:
            return False, 5.0  # 5 second delay for re-enable.
        if self.model.run_immediately:
            # figure out when the schedule would run next anyway
            _, n = self.schedule.is_due(self.last_run_at)
            return True, n
        return self.schedule.is_due(self.last_run_at)

    def _default_now(self):
        return self.app.now()

    def __next__(self):
        self.model.last_run_at = self.app.now()
        self.model.total_run_count += 1
        self.model.run_immediately = False
        return self.__class__(self.model)

    next = __next__  # for 2to3

    def save(self, session):
        obj = PeriodicTask.filter_by(session, id=self.model.id).first()
        for field in self.save_fields:
            setattr(obj, field, getattr(self.model, field))
        self.save_model(session, obj)

    @staticmethod
    def save_model(session, obj):
        session.add(obj)

    @classmethod
    def to_schedule(cls, schedule):
        """
        :param schedule:
        :return:
        """
        for schedule_type, schedule_model, schedule_name in cls.model_schedules:
            schedule = schedules.maybe_schedule(schedule)
            if isinstance(schedule, schedule_type):
                schedule_field = schedule_model.from_schedule(schedule).dumps()
                return schedule_field, schedule_name
        else:
            raise ValueError('Cannot convert schedule type {0!r} to model'.format(schedule))

    @classmethod
    def from_entry(cls, name, session, skip_fields=('relative', 'options'), **entry):
        """
        创建或者更新PeriodicTask
        :param session:
        :param name:
        :param skip_fields:
        :param entry:
        :return:
        """
        fields = dict(entry)
        for skip_field in skip_fields:
            fields.pop(skip_field, None)
        schedule = fields.pop('schedule')
        schedule_field, schedule_name = cls.to_schedule(schedule)
        fields[schedule_name] = schedule_field
        fields['args'] = json.dumps(fields.get('args') or [])
        fields['kwargs'] = json.dumps(fields.get('kwargs') or {})
        model, _ = PeriodicTask.update_or_create(session, name=name, defaults=fields)
        cls.save_model(session, model)
        return cls(model)

    def __repr__(self):
        return '<ModelEntry: {0} {1}(*{2}, **{3}) {{4}}>'.format(
            safe_str(self.name), self.task, self.args, self.kwargs, self.schedule,
        )


class DatabaseScheduler(Scheduler):
    sync_every = 1 * 60
    UPDATE_INTERVAL = datetime.timedelta(seconds=5)

    Entry = ModelEntry
    Model = PeriodicTask
    _schedule = None
    _last_timestamp = None
    _initial_read = False

    def __init__(self, session=None, *args, **kwargs):
        self._last_updated = None
        self.session = session or get_session()
        self._dirty = set()
        self._finalize = Finalize(self, self.sync, exitpriority=5)
        super(DatabaseScheduler, self).__init__(*args, **kwargs)
        self.max_interval = (kwargs.get('max_interval') or
                             self.app.conf.CELERYBEAT_MAX_LOOP_INTERVAL or
                             DEFAULT_MAX_INTERVAL)

    def setup_schedule(self):
        self.install_default_entries(self.schedule)
        self.update_from_dict(self.app.conf.CELERYBEAT_SCHEDULE)

    def all_as_schedule(self):
        debug('DatabaseScheduler: Fetching database schedule')
        s = {}
        try:
            for model in self.Model.filter_by(self.session, enabled=True).all():
                try:
                    s[model.name] = self.Entry(model)
                except ValueError:
                    pass
            return s
        except sqlalchemy.exc.OperationalError as exc:
            error(exc)
            return {}

    def reserve(self, entry):
        new_entry = Scheduler.reserve(self, entry)
        # Need to store entry by name, because the entry may change
        # in the mean time.
        self._dirty.add(new_entry.name)
        return new_entry

    def sync(self):
        debug('Writing entries...\n dirty objects: {}'.format(self._dirty))
        _tried = set()
        while self._dirty:
            try:
                name = self._dirty.pop()
                _tried.add(name)
                self.schedule[name].save(self.session)
            except sqlalchemy.exc.OperationalError as exc:
                error(exc)
            except KeyError:
                pass

    def update_from_dict(self, dict_):
        s = {}
        for name, entry in dict_.items():
            try:

                s[name] = self.Entry.from_entry(name, self.session, **entry)
            except Exception as exc:
                error(ADD_ENTRY_ERROR, name, exc, entry)
        self.schedule.update(s)

    def install_default_entries(self, data):
        entries = {}
        if self.app.conf.CELERY_TASK_RESULT_EXPIRES:
            entries.setdefault(
                'celery.backend_cleanup', {
                    'task': 'celery.backend_cleanup',
                    'schedule': schedules.crontab('0', '4', '*'),
                    'options': {'expires': 12 * 3600},
                },
            )
        self.update_from_dict(entries)

    def requires_update(self):
        """check whether we should pull an updated schedule
        from the backend database"""
        if not self._last_updated:
            return True
        return self._last_updated + self.UPDATE_INTERVAL < datetime.datetime.now()

    @property
    def schedule(self):
        if self.requires_update():
            self.sync()
            self._schedule = self.all_as_schedule()
            debug('Current schedule:\n%s', '\n'.join(repr(entry) for entry in self._schedule.itervalues()))
        return self._schedule
