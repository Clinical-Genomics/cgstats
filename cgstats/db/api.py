# -*- coding: utf-8 -*-
import logging
import pkg_resources

from alchy import Manager
from sqlalchemy import func

from .models import Model, Sample, Flowcell, Demux, Datasource, Unaligned, Project
from sqlalchemy import or_

SAMPLE_PATTERN = "{}\_%"
log = logging.getLogger(__name__)


def connect(uri):
    """Connect to the database."""
    for models in pkg_resources.iter_entry_points('cgstats.models.1'):
        models.load()
    log.debug('open connection to database: %s', uri)
    manager = Manager(config=dict(SQLALCHEMY_DATABASE_URI=uri), Model=Model,
                      session_options=dict(autoflush=False))
    return manager


def get_sample(sample_id):
    """Get a unique demux sample."""
    pattern = SAMPLE_PATTERN.format(sample_id)
    query = Sample.query.filter(or_(Sample.samplename.like(pattern),
                                    Sample.samplename == sample_id))
    return query


def flowcells(sample=None):
    """Return a query for the latest flowcells."""
    query = (Flowcell.query.join(Flowcell.datasource, Demux.datasource)
                           .order_by(Datasource.rundate.desc()))
    if sample:
        pattern = SAMPLE_PATTERN.format(sample)
        query = (query.join(Demux.unaligned, Unaligned.sample)
                      .filter(or_(Sample.samplename.like(pattern),
                                  Sample.samplename == sample)))
    return query


def samples(flowcell_name=None):
    """Return a query for the latest samples."""
    query = (Sample.query.join(Sample.unaligned, Unaligned.demux,
                               Demux.flowcell))
    if flowcell_name:
        query = query.filter(Flowcell.flowcellname == flowcell_name)
    return query


def select(flowcell, project_name=None):
    """Return a query for the stats"""

#    query = """ SELECT sample.samplename AS smp, flowcell.flowcellname AS flc, 
#    GROUP_CONCAT(unaligned.lane ORDER BY unaligned.lane) AS lanes, 
#    GROUP_CONCAT(unaligned.readcounts ORDER BY unaligned.lane) AS rds, SUM(unaligned.readcounts) AS readsum, 
#    GROUP_CONCAT(unaligned.yield_mb ORDER BY unaligned.lane) AS yield, SUM(unaligned.yield_mb) AS yieldsum, 
#    GROUP_CONCAT(TRUNCATE(q30_bases_pct,2) ORDER BY unaligned.lane) AS q30, 
#    GROUP_CONCAT(TRUNCATE(mean_quality_score,2) ORDER BY unaligned.lane) AS meanq
#    FROM sample, flowcell, unaligned, project, demux
#    WHERE sample.sample_id = unaligned.sample_id 
#    AND flowcell.flowcell_id = demux.flowcell_id
#    AND unaligned.demux_id = demux.demux_id 
#    AND sample.project_id = project.project_id
#    AND project.projectname = '""" + proje + """' 
#    AND flowcell.flowcellname = '""" + flowc + """'
#    GROUP BY samplename, flowcell.flowcell_id 
#    ORDER BY lane, sample.samplename, flowcellname """

    query = (Sample.query.join(Sample.unaligned, Unaligned.demux, Demux.flowcell))
    if project_name:
        query = (query.join(Sample.project).filter(Project.projectname == project_name))

    query = query.with_entities(
                  Sample.samplename, Flowcell.flowcellname,
                  func.group_concat(Unaligned.lane.op('ORDER BY')(Unaligned.lane)).label('lanes'),
                  func.group_concat(
                      Unaligned.readcounts.op('ORDER BY')(Unaligned.lane)).label('reads'),
                  func.sum(Unaligned.readcounts).label('readsum'),
                  func.group_concat(
                      Unaligned.yield_mb.op('ORDER BY')(Unaligned.lane)).label('yld'),
                  func.sum(Unaligned.yield_mb).label('yieldsum'),
                  func.group_concat(
                      func.truncate(Unaligned.q30_bases_pct, 2)
                      .op('ORDER BY')(Unaligned.lane)).label('q30'),
                  func.group_concat(
                      func.truncate(Unaligned.mean_quality_score, 2)
                      .op('ORDER BY')(Unaligned.lane)).label('meanq'),
            )

    query = query.filter(Flowcell.flowcellname == flowcell)
    query = query.group_by(Sample.samplename, Flowcell.flowcell_id)
    query = query.order_by(Unaligned.lane, Sample.samplename, Flowcell.flowcellname)

    return query

