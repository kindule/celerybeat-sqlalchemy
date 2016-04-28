#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#=============================================================================
#     FileName: example
#         Desc:
#       Author: ge.jin
#        Email: ge.jin@woqutech.com
#     HomePage: wwww.woqutech.com
#      Version: 0.0.1
#   LastChange: 4/27/16 11:38 AM
#      History:
#=============================================================================
'''
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

engine = create_engine('mysql+mysqldb://root:letsg0@127.0.0.1/celerybeat', pool_recycle=3600, echo=True)
Session = sessionmaker(bind=engine)


class User(Base):

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(length=20))
    fullname = Column(String(length=20))
    password = Column(String(length=20))
    addresses = relationship('Address')

    def __repr__(self):
        return "<User(name='%s', fullname='%s', password='%s')>" % (self.name, self.fullname, self.password)


class Address(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    email_address = Column(String(length=20), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="addresses")

    def __repr__(self):
        return "<Address(email_address='%s')>" % self.email_address


Base.metadata.create_all(engine)
session = Session()
ed_user = User(name='ed', fullname='Ed Jones', password='edspassword')
session.commit()
