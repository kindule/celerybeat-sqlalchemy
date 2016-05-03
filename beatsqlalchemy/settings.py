#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#=============================================================================
#     FileName: settings
#         Desc:
#       Author: ge.jin
#        Email: ge.jin@woqutech.com
#     HomePage: wwww.woqutech.com
#      Version: 0.0.1
#   LastChange: 4/28/16 9:13 AM
#      History:
#=============================================================================
'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('mysql+mysqldb://root:letsg0@127.0.0.1/celerybeat',
                       pool_recycle=3600,
                       echo=False)
Session = sessionmaker(bind=engine)

CELERYBEAT_SCHEDULER = 'beatsqlalchemy.schedulers.DatabaseScheduler'
