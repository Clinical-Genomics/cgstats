# -*- coding: utf-8 -*-
import logging
import pkg_resources

from alchy import Manager

from .models import Model, Sample, Flowcell, Demux, Datasource, Unaligned

log = logging.getLogger(__name__)


def connect(uri):
    """Connect to the database."""
    for models in pkg_resources.iter_entry_points('clinstatsdb.models.1'):
        models.load()
    log.debug('open connection to database: %s', uri)
    manager = Manager(config=dict(SQLALCHEMY_DATABASE_URI=uri), Model=Model)
    return manager


def get_sample(sample_id):
    """Get a unique demux sample."""
    pattern = "{}\_%".format(sample_id)
    query = Sample.query.filter(Sample.samplename.like(pattern))
    return query


def flowcells():
    """Return a query for the latest flowcells."""
    query = (Flowcell.query.join(Flowcell.datasource, Demux.datasource)
                           .order_by(Datasource.rundate.desc()))
    return query


def samples(flowcell_name=None):
    """Return a query for the latest samples."""
    query = (Sample.query.join(Sample.unaligned, Unaligned.demux,
                               Demux.flowcell))
    if flowcell_name:
        query = query.filter(Flowcell.flowcellname == flowcell_name)
    return query
