# -*- coding: utf-8 -*-
PROJECT_NAME = __name__.split('.')[0]

class BaseConfig:
    PROJECT = PROJECT_NAME
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = ""
