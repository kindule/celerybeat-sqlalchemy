A beatsqlalchemy project
===============================

A beatsqlalchemy project.

This is a Celery Beat Scheduler (http://celery.readthedocs.org/en/latest/userguide/periodic-tasks.html)
that stores both the schedules themselves and their status
information in a backend SQLAlchemy database. It can be installed by
installing the beatsqlalchemy Python egg::

Feature
=======

#. 后端使用SQLAlchemy（原生Celerybeat使用的是文本文件）
#. 支持crontab方式和interval方式调度task
#. 动态增加和删除task

Installation
============

::

    $ pip install -U git+ssh://git@192.168.1.121/qtools/beatsqlalchemy.git

or with version::

    $ pip install -U git+ssh://git@192.168.1.121/qtools/beatsqlalchemy.git@tag-1.0.1



Quick start
===========

And specifying the scheduler when running Celery Beat, e.g.::

    $ celery beat -S beatsqlalchemy.schedulers.DatabaseScheduler

Settings for the scheduler are defined in your celery configuration file
similar to how other aspects of Celery are configured::

    BEAT_SQLAlchemy_URL = "mysql+mysqldb://root:letsg0@192.168.99.100:3307/celerybeat?charset=utf8"

You will then want to create the necessary tables. Go to the contrib directory and use create_table for necessary tables.

    python create_table.py


If no settings are specified, the library will attempt to use the
**schedules** collection in the local **celery** database.

Schedules can be manipulated in the SQLALChemy database.There exist two types of schedules,
interval and crontab.


The following fields are required: name, task, crontab || interval,
enabled when defining new tasks.
total_run_count and last_run_at are maintained by the
scheduler and should not be externally manipulated.

The example from Celery User Guide::Periodic Tasks.
(see: http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html#crontab-schedules)::

	{

		CELERYBEAT_SCHEDULE = {
		    # Executes every Monday morning at 7:30 A.M
		    'add-every-monday-morning': {
		        'task': 'tasks.add',
		        'schedule': crontab(hour=7, minute=30, day_of_week=1),
		        'args': (16, 16),
		    },
		}
	}

addtask example::

    import json

    from celery import Celery, current_app

    app = Celery('celerybeat-sqlalchemy')
    app.config_from_object('settings')
    from model import PeriodicTask, get_session

    session = get_session()
    pt, _ = PeriodicTask.update_or_create(session_obj=session, name="tasks.boardcast_to", task="tasks.boardcast_to",
                                          defaults=dict(crontab=json.dumps({'minute': '*/1'}),
                                                        args='[1,3,4,"a"]',
                                                        kwargs='{"pp":"workd"}',
                                                        queue="noexist",
                                                        exchange=""))
    session.add(pt)
    session.flush()


    pt, _ = PeriodicTask.update_or_create(session_obj=session, name="tasks.direct_to", task="tasks.direct_to",
                                          interval=json.dumps({'every': 30, 'period': 'seconds'}),
                                          defaults=dict(args='[1,2,3,4]', kwargs='{"hello":"world"}'))
    session.add(pt)
    session.flush()
    print pt.schedule
