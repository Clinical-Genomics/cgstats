# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from .models import db


def connect(connection_string):
    """Connect to the database."""
    engine = create_engine(connection_string)
    db.metadata.bind = engine
    session = scoped_session(sessionmaker(bind=engine))
    db.query = session.query
    return session
