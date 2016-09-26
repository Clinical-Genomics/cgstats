# -*- coding: utf-8 -*-
import logging
import pkg_resources

from alchy import Manager

from .models import Model

log = logging.getLogger(__name__)


def connect(uri):
    """Connect to the database."""
    for models in pkg_resources.iter_entry_points('clinstatsdb.models.1'):
        models.load()
    log.debug('open connection to database: %s', uri)
    manager = Manager(config=dict(SQLALCHEMY_DATABASE_URI=uri), Model=Model)
    return manager
