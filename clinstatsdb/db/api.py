# -*- coding: utf-8 -*-
import logging

from alchy import Manager

from .models import Model

log = logging.getLogger(__name__)


def connect(uri):
    """Connect to the database."""
    log.debug('open connection to database: %s', uri)
    manager = Manager(config=dict(SQLALCHEMY_DATABASE_URI=uri), Model=Model)
    return manager
