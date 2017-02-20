# -*- coding: utf-8 -*-
import logging
import pkg_resources

from alchy import Manager

from .models import Model, Sample, Flowcell, Demux, Datasource, Unaligned

SAMPLE_PATTERN = "{}\_%"
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
    pattern = SAMPLE_PATTERN.format(sample_id)
    query = Sample.query.filter(Sample.samplename.like(pattern))
    if query.first() is None:
        log.info("no results found, trying alternative query")
        query = Sample.query.filter_by(samplename=sample_id)
    return query


def flowcells(sample=None):
    """Return a query for the latest flowcells."""
    query = (Flowcell.query.join(Flowcell.datasource, Demux.datasource)
                           .order_by(Datasource.rundate.desc()))
    if sample:
        pattern = SAMPLE_PATTERN.format(sample)
        query = (query.join(Demux.unaligned, Unaligned.sample)
                      .filter(Sample.samplename.like(pattern)))
        if query.first() is None:
            log.info("no results found, trying alternative query")
            query = (query.join(Demux.unaligned, Unaligned.sample)
                          .filter(Sample.samplename=sample))
    return query


def samples(flowcell_name=None):
    """Return a query for the latest samples."""
    query = (Sample.query.join(Sample.unaligned, Unaligned.demux,
                               Demux.flowcell))
    if flowcell_name:
        query = query.filter(Flowcell.flowcellname == flowcell_name)
    return query
