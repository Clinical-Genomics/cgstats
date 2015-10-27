#!/usr/bin/env python
# encoding: utf-8

from ..db import db, SQL, config
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey, UniqueConstraint, Numeric, Date
from sqlalchemy.orm import relationship, backref

class Project(db):
    __tablename__ = 'project'

    project_id = Column(Integer, primary_key=True)
    projectname = Column(String(255), nullable=False)
    time = Column(DateTime, nullable=False)

    def __repr__(self):
        return (u'{self.__class__.__name__}: {self.project_id}'.format(self=self))

class Sample(db):
    __tablename__ = 'sample'

    sample_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('project.project_id'), nullable=False)
    samplename = Column(String(255), nullable=False)
    barcode = Column(String(255), nullable=True)
    time = Column(DateTime, nullable=True)

    project = relationship('Project', backref=backref('samples'))

class Supportparams(db):
    __tablename__ = 'supportparams'

    supportparams_id = Column(Integer, primary_key=True)
    document_path = Column(String(255), nullable=False)
    systempid = Column(String(255), nullable=True)
    systemos = Column(String(255), nullable=True)
    systemperlv = Column(String(255), nullable=True)
    systemperlexe = Column(String(255), nullable=True)
    idstring = Column(String(255), nullable=True)
    program = Column(String(255), nullable=True)
    commandline = Column(Text)
    sampleconfig_path = Column(String(255), nullable=True)
    sampleconfig = Column(Text)
    time = Column(DateTime, nullable=True)

class Datasource(db):
    __tablename__ = 'datasource'

    datasource_id = Column(Integer, primary_key=True)
    supportparams_id = Column(Integer, ForeignKey('supportparams.supportparams_id'), nullable=False)
    runname = Column(String(255), nullable=True)
    machine = Column(String(255), nullable=True)
    rundate = Column(DateTime, nullable=True)
    document_path = Column(String(255), nullable=False)
    document_type = Column(Enum('html', 'xml', 'undefined'), nullable=False, default='html')
    server = Column(String(255), nullable=True)
    time = Column(DateTime, nullable=True)

    supportparams = relationship('Supportparams', backref=backref('datasources'))

    def __repr__(self):
        return (u'{self.__class__.__name__}: {self.runname}'.format(self=self))

class Demux(db):
    __tablename__ = 'demux'

    demux_id = Column(Integer, primary_key=True)
    flowcell_id = Column(Integer, ForeignKey('flowcell.flowcell_id'), nullable=False)
    datasource_id = Column(Integer, ForeignKey('datasource.datasource_id'), nullable=False)
    basemask = Column(String(255), nullable=True)
    time = Column(DateTime, nullable=True)

    UniqueConstraint('flowcell', 'basemask', name='demux_ibuk_1')

    datasource = relationship('Datasource', backref=backref('demuxes'))
    datasource = relationship('Flowcell', backref=backref('demuxes'))

class Flowcell(db):
    __tablename__ = 'flowcell'

    flowcell_id = Column(Integer, primary_key=True)
    flowcellname = Column(String(255), nullable=False)
    flowcell_pos = Column(Enum('A', 'B'), nullable=False)
    time_start = Column(DateTime, nullable=True)
    time_end = Column(DateTime, nullable=True)
    time = Column(DateTime)

    UniqueConstraint('flowcellname', name='flowcellname')

    datasource = relationship('Demux', backref=backref('flowcells'))

class Unaligned(db):
    __tablename__ = 'unaligned'

    unaligned_id = Column(Integer, primary_key=True)
    sample_id = Column(Integer, ForeignKey('sample.sample_id'), nullable=False)
    demux_id = Column(Integer, ForeignKey('demux.demux_id'), nullable=False)
    lane = Column(Integer, nullable=True)
    yield_mb = Column(Integer, nullable=True)
    passed_filter_pct = Column(Numeric(10,5), nullable=True)
    readcounts = Column(Integer, nullable=True)
    raw_clusters_per_lane_pct = Column(Numeric(10,5), nullable=True)
    perfect_indexreads_pct = Column(Numeric(10,5), nullable=True)
    q30_bases_pct = Column(Numeric(10,5), nullable=True)
    mean_quality_score = Column(Numeric(10,5), nullable=True)
    time = Column(DateTime, nullable=True)

    demux = relationship('Demux', backref=backref('unaligned'))
    sample = relationship('Sample', backref=backref('unaligned'))

class Backup(db):
    __tablename__ = 'backup'

    runname = Column(String(255), primary_key=True)
    startdate = Column(Date, nullable=False)
    nas = Column(String(255), nullable=True)
    nasdir = Column(String(255), nullable=True)
    starttonas = Column(DateTime, nullable=True)
    endtonas = Column(DateTime, nullable=True)
    preproc = Column(String(255), nullable=True)
    preprocdir = Column(String(255), nullable=True)
    startpreproc = Column(DateTime, nullable=True)
    endpreproc = Column(DateTime, nullable=True)
    frompreproc = Column(DateTime, nullable=True)
    analysis = Column(String(255), nullable=True)
    analysisdir = Column(String(255)    , nullable=True)
    toanalysis = Column(DateTime, nullable=True)
    fromanalysis = Column(DateTime, nullable=True)
    backup = Column(String(255), nullable=True)
    backupdir = Column(String(255), nullable=True)
    tobackup = Column(DateTime, nullable=True)
    frombackup = Column(DateTime, nullable=True)
    tape = Column(String(255), nullable=True)
    tapedir = Column(String(255), nullable=True)
    totape = Column(DateTime, nullable=True)
    fromtape = Column(DateTime, nullable=True)

class Version(db):
    __tablename__ = 'version'

    version_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=True)
    major = Column(Integer, nullable=True)
    minor = Column(Integer, nullable=True)
    patch = Column(Integer, nullable=True)
    comment = Column(String(255), nullable=True)
    time = Column(DateTime, nullable=True)

    UniqueConstraint('name', 'major', 'minor', 'patch', name='flowcellname')

    @classmethod
    def get_version(cls):
        """Retrieves the database version
        Returns (tuple): (major, minor, patch, name)
        """

        """ SELECT major, minor, patch, name FROM version ORDER BY time DESC LIMIT 1 """
        return SQL.query(
            Version.major.label('major'),\
            Version.minor.label('minor'),\
            Version.patch.label('patch'),\
            Version.name.label('name')).\
        order_by(Version.time.desc()).\
        limit(1).\
        one()

    @classmethod
    def check(cls, dbname, ver):
        """Checks version of database against dbname and version [normally from the config file]

        Args:
          dbname (str): database name as stored in table version
          ver (str): version string in the format major.minor.patch

        Returns:
          True: if identical
        """
        rs = cls.get_version()
        if rs is not None:
            return ('{0}.{1}.{2}'.format(str(rs.major), str(rs.minor), str(rs.patch)) == ver and dbname == rs.name)


    @classmethod
    def latest(cls):
        """Checks if the latest version in the settings file matches with the DB
        Returns: True if identical

        """
        return cls.check(config['clinstats']['name'], config['clinstats']['version'])
