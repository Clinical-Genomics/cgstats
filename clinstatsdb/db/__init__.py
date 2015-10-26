#!/usr/bin/env python
# encoding: utf-8

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from ..settings import BaseConfig 

config = BaseConfig()
db = declarative_base()

engine = create_engine(config.get['connection_string'])
Session = sessionmaker()
Session.configure(bind=engine)
SQL = Session()
