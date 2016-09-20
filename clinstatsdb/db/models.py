#!/usr/bin/env python
# encoding: utf-8
from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Index, Integer, Numeric, String, Text, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.declarative import declarative_base

db = declarative_base()
metadata = db.metadata


class Backup(db):
    __tablename__ = 'backup'

    runname = Column(String(255), primary_key=True)
    startdate = Column(Date, nullable=False)
    nas = Column(String(255))
    nasdir = Column(String(255))
    starttonas = Column(DateTime)
    endtonas = Column(DateTime)
    preproc = Column(String(255))
    preprocdir = Column(String(255))
    startpreproc = Column(DateTime)
    endpreproc = Column(DateTime)
    frompreproc = Column(DateTime)
    analysis = Column(String(255))
    analysisdir = Column(String(255))
    toanalysis = Column(DateTime)
    fromanalysis = Column(DateTime)
    inbackupdir = Column(Integer, server_default=text("'0'"))
    backuptape_id = Column(ForeignKey(u'backuptape.backuptape_id'))
    backupdone = Column(DateTime)
    md5done = Column(DateTime)

    backuptape = relationship(u'Backuptape')


class Backuptape(db):
    __tablename__ = 'backuptape'

    backuptape_id = Column(Integer, primary_key=True)
    tapedir = Column(String(255))
    nametext = Column(Text)
    tapedate = Column(DateTime)


class Datasource(db):
    __tablename__ = 'datasource'

    datasource_id = Column(Integer, primary_key=True)
    supportparams_id = Column(ForeignKey(u'supportparams.supportparams_id'), nullable=False)
    runname = Column(String(255))
    machine = Column(String(255))
    rundate = Column(Date)
    document_path = Column(String(255), nullable=False)
    document_type = Column(Enum(u'html', u'xml', u'undefined'), nullable=False, server_default=text("'html'"))
    server = Column(String(255))
    time = Column(DateTime)

    supportparams = relationship(u'Supportparam')


class Demux(db):
    __tablename__ = 'demux'
    __table_args__ = (
        Index('demux_ibuk_1', 'flowcell_id', 'basemask', unique=True),
    )

    demux_id = Column(Integer, primary_key=True)
    flowcell_id = Column(ForeignKey(u'flowcell.flowcell_id'), nullable=False)
    datasource_id = Column(ForeignKey(u'datasource.datasource_id'), nullable=False)
    basemask = Column(String(255))
    time = Column(DateTime)

    datasource = relationship(u'Datasource')
    flowcell = relationship(u'Flowcell')


class Flowcell(db):
    __tablename__ = 'flowcell'

    flowcell_id = Column(Integer, primary_key=True)
    flowcellname = Column(String(9), nullable=False, unique=True)
    flowcell_pos = Column(Enum(u'A', u'B'), nullable=False)
    hiseqtype = Column(String(255), server_default=text("'hiseqga'"))
    time = Column(DateTime)


class Project(db):
    __tablename__ = 'project'

    project_id = Column(Integer, primary_key=True)
    projectname = Column(String(255), nullable=False)
    comment = Column(Text)
    time = Column(DateTime)


class Sample(db):
    __tablename__ = 'sample'

    sample_id = Column(Integer, primary_key=True)
    project_id = Column(ForeignKey(u'project.project_id'), nullable=False)
    samplename = Column(String(255), nullable=False)
    customerid = Column(String(255))
    limsid = Column(String(255))
    barcode = Column(String(255))
    time = Column(DateTime)

    project = relationship(u'Project')


class Supportparam(db):
    __tablename__ = 'supportparams'

    supportparams_id = Column(Integer, primary_key=True)
    document_path = Column(String(255), nullable=False)
    systempid = Column(String(255))
    systemos = Column(String(255))
    systemperlv = Column(String(255))
    systemperlexe = Column(String(255))
    idstring = Column(String(255))
    program = Column(String(255))
    commandline = Column(Text)
    sampleconfig_path = Column(String(255))
    sampleconfig = Column(Text)
    time = Column(DateTime)


class Unaligned(db):
    __tablename__ = 'unaligned'

    unaligned_id = Column(Integer, primary_key=True)
    sample_id = Column(ForeignKey(u'sample.sample_id'))
    demux_id = Column(ForeignKey(u'demux.demux_id'))
    lane = Column(Integer)
    yield_mb = Column(Integer)
    passed_filter_pct = Column(Numeric(10, 5))
    readcounts = Column(Integer)
    raw_clusters_per_lane_pct = Column(Numeric(10, 5))
    perfect_indexreads_pct = Column(Numeric(10, 5))
    q30_bases_pct = Column(Numeric(10, 5))
    mean_quality_score = Column(Numeric(10, 5))
    time = Column(DateTime)
    approved = Column(Integer)

    demux = relationship(u'Demux')
    sample = relationship(u'Sample')


class Version(db):
    __tablename__ = 'version'

    version_id = Column(Integer, primary_key=True)
    name = Column(String(255))
    major = Column(Integer)
    minor = Column(Integer)
    patch = Column(Integer)
    comment = Column(String(255))
    time = Column(DateTime, nullable=False)
