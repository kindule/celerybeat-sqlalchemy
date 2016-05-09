#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#=============================================================================
#     FileName: __init__.py
#         Desc:
#       Author: ge.jin
#        Email: ge.jin@woqutech.com
#     HomePage: wwww.woqutech.com
#      Version: 0.0.1
#   LastChange: 4/28/16 9:30 AM
#      History:
#=============================================================================
'''
from contextlib import contextmanager

from .model import PeriodicTask
from celery import current_app
from sqlalchemy import event
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy.schema import MetaData

engine = create_engine(current_app.conf.BEAT_SQLAlchemy_URL, pool_size=20, pool_recycle=3600, echo=False)
Session = sessionmaker(bind=engine, autocommit=True)
metadata = MetaData(bind=engine)


def get_session():
    return Session()


@contextmanager
def open_session():
    try:
        new_session = Session()
        yield new_session
        new_session.commit()
    except OperationalError as e:
        # create all table
        metadata.create_all(checkfirst=True)
        new_session.commit()
    except Exception as e:
        new_session.rollback()
        raise e
    finally:
        new_session.close()


class ConstrainError(Exception):
    pass


@event.listens_for(Session, "before_flush")
def before_flush(session, flush_context, instances):
    for obj in session.new | session.dirty:
        if isinstance(obj, PeriodicTask):
            if not obj.interval and not obj.crontab:
                raise ConstrainError('One of interval or crontab must be set.')
            if obj.interval and obj.crontab:
                raise ConstrainError('Only one of interval or crontab must be set')
