#!/usr/bin/env python
# encoding: utf-8
from sqlalchemy import (Column, Integer, String, DateTime, Text, Enum,
                        ForeignKey, UniqueConstraint, Numeric, Date)
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.declarative import declarative_base

db = declarative_base()


class Project(db):
    __tablename__ = 'project'

    project_id = Column(Integer, primary_key=True)
    projectname = Column(String(255), nullable=False)
    time = Column(DateTime, nullable=False)

    def __repr__(self):
        return (u"{self.__class__.__name__}: {self.project_id}"
                .format(self=self))

    @classmethod
    def exists(cls, project_name):
        """Checks if the Prohect entry already exists

        Args:
            project_name (str): project name without the Project_ prefix

        Returns:
            int: project_id on exists
            False: on not exists

        """
        try:
            rs = (cls.query(cls.project_id.label('id'))
                     .filter(cls.projectname == project_name).one())
            return rs.id
        except NoResultFound:
            return False


class Sample(db):
    __tablename__ = 'sample'

    sample_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('project.project_id'),
                        nullable=False)
    samplename = Column(String(255), nullable=False)
    barcode = Column(String(255), nullable=True)
    time = Column(DateTime, nullable=True)

    project = relationship('Project', backref=backref('samples'))

    @property
    def lims_id(self):
        """Parse out the LIMS id from the samplename in demux database."""
        sample_part = self.samplename.split('_')[0]
        sanitized_id = sample_part.rstrip('FB')
        return sanitized_id

    @classmethod
    def exists(cls, sample_name, barcode):
        """Checks if a Sample entry already exists

        Args:
            sample_name (str): sample name without Sample_ prefix but with
                               index identifier _nxdual9
            barcode (str): the index

        Returns:
            int: sample_id on exists
            False: on not exists

        """
        try:
            rs = (cls.query(cls.sample_id.label('id'))
                     .filter(cls.samplename == sample_name)
                     .filter(cls.barcode == barcode).one())
            return rs.id
        except NoResultFound:
            return False


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

    @classmethod
    def exists(cls, document_path):
        """Checks if the supportparams entry already exists

        Args:
            document_path (str): Full path to the Unaligned directory

        Returns:
            int: supportparams_id on exists
            False: on not exists

        """
        try:
            rs = (cls.query(cls.supportparams_id.label('id'))
                     .filter(cls.document_path == document_path).one())
            return rs.id
        except NoResultFound:
            return False


class Datasource(db):
    __tablename__ = 'datasource'

    datasource_id = Column(Integer, primary_key=True)
    supportparams_id = Column(Integer,
                              ForeignKey('supportparams.supportparams_id'),
                              nullable=False)
    runname = Column(String(255), nullable=True)
    machine = Column(String(255), nullable=True)
    rundate = Column(DateTime, nullable=True)
    document_path = Column(String(255), nullable=False)
    document_type = Column(Enum('html', 'xml', 'undefined'), nullable=False,
                           default='html')
    server = Column(String(255), nullable=True)
    time = Column(DateTime, nullable=True)

    supportparams = relationship('Supportparams',
                                 backref=backref('datasources'))

    def __repr__(self):
        return (u'{self.__class__.__name__}: {self.runname}'.format(self=self))

    @classmethod
    def exists(cls, document_path):
        """Checks if the Datasource entry already exists

        Args:
            document_path (str): Full path to the stats file

        Returns:
            int: datasource_id on exists
            False: on not exists

        """
        try:
            rs = (cls.query(cls.supportparams_id.label('id'))
                     .filter(cls.document_path == document_path).one())
            return rs.id
        except NoResultFound:
            return False


class Demux(db):
    __tablename__ = 'demux'

    demux_id = Column(Integer, primary_key=True)
    flowcell_id = Column(Integer, ForeignKey('flowcell.flowcell_id'),
                         nullable=False)
    datasource_id = Column(Integer, ForeignKey('datasource.datasource_id'),
                           nullable=False)
    basemask = Column(String(255), nullable=True)
    time = Column(DateTime, nullable=True)

    UniqueConstraint('flowcell', 'basemask', name='demux_ibuk_1')

    datasource = relationship('Datasource', backref=backref('demuxes'))
    flowcell = relationship('Flowcell', backref=backref('demuxes'))

    @classmethod
    def exists(cls, flowcell_id, basemask):
        """Checks if the Demux entry already exists

        Args:
            flowcell_id (int): flowcell_id in the table Flowcell
            basemask (str): the basemask used to demux, e.g. Y101,I6n,Y101

        Returns:
            int: demux_id on exists
            False: on not exists

        """
        try:
            rs = (cls.query(cls.demux_id.label('id'))
                     .filter(cls.flowcell_id == flowcell_id)
                     .filter(cls.basemask == basemask).one())
            return rs.id
        except NoResultFound:
            return False


class Flowcell(db):
    __tablename__ = 'flowcell'

    flowcell_id = Column(Integer, primary_key=True)
    flowcellname = Column(String(255), nullable=False)
    flowcell_pos = Column(Enum('A', 'B'), nullable=False)
    time = Column(DateTime)

    UniqueConstraint('flowcellname', name='flowcellname')

    datasource = relationship('Demux', backref=backref('flowcells'))

    @classmethod
    def exists(cls, flowcell_name):
        """Checks if the Flowcell entry already exists

        Args:
            flowcell_name (str): The name of the flowcell

        Returns:
            int: flowcell_id on exists
            False: on not exists

        """
        try:
            rs = (cls.query(cls.flowcell_id.label('id'))
                     .filter(cls.flowcellname == flowcell_name).one())
            return rs.id
        except NoResultFound:
            return False


class Unaligned(db):
    __tablename__ = 'unaligned'

    unaligned_id = Column(Integer, primary_key=True)
    sample_id = Column(Integer, ForeignKey('sample.sample_id'), nullable=False)
    demux_id = Column(Integer, ForeignKey('demux.demux_id'), nullable=False)
    lane = Column(Integer, nullable=True)
    yield_mb = Column(Integer, nullable=True)
    passed_filter_pct = Column(Numeric(10, 5), nullable=True)
    readcounts = Column(Integer, nullable=True)
    raw_clusters_per_lane_pct = Column(Numeric(10, 5), nullable=True)
    perfect_indexreads_pct = Column(Numeric(10, 5), nullable=True)
    q30_bases_pct = Column(Numeric(10, 5), nullable=True)
    mean_quality_score = Column(Numeric(10, 5), nullable=True)
    time = Column(DateTime, nullable=True)

    demux = relationship('Demux', backref=backref('unaligned'))
    sample = relationship('Sample', backref=backref('unaligned'))

    @classmethod
    def exists(cls, sample_id, demux_id, lane):
        """Checks if an Unaligned entry already exists

        Args:
            sample_id (int): sample id
            demux_id (int): demux id
            lane (int): lane in which the sample ran

        Returns:
            int: unaligned_id on exists
            False: on not exists

        """
        try:
            rs = (cls.query(cls.unaligned_id.label('id'))
                     .filter(cls.sample_id == sample_id)
                     .filter(cls.demux_id == demux_id)
                     .filter(cls.lane == lane).one())
            return rs.id
        except NoResultFound:
            return False


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
    analysisdir = Column(String(255), nullable=True)
    toanalysis = Column(DateTime, nullable=True)
    fromanalysis = Column(DateTime, nullable=True)
    inbackupdir = Column(TINYINT, nullable=True)
    backuptape_id = Column(Integer, ForeignKey('backuptape.backuptape_id'),
                           nullable=False)
    backupdone = Column(DateTime, nullable=True)
    md5done = Column(DateTime, nullable=True)

    tape = relationship('Backuptape', backref=backref('backup'))

    @classmethod
    def exists(cls, runname, tapedir=None):
        """Check if run is already backed up. Optionally: checks if run is
        on certain tape

        Args:
            runname (str): e.g. 151117_D00410_0187_AHWYGMADXX
            tapedir (str): the name of the tape, e.g. tape036_037

        Returns:
            int: runname on exists
            False: on not exists
        """
        try:
            if tapedir is not None:
                rs = (cls.query(cls.runname.label('runname'))
                         .outerjoin(Backuptape)
                         .filter(cls.runname == runname)
                         .filter(Backuptape.tapedir == tapedir).one())
            else:
                rs = (cls.query(cls.runname.label('runname'))
                         .filter(cls.runname == runname).one())
            return rs.runname
        except NoResultFound:
            return False


class Backuptape(db):
    __tablename__ = 'backuptape'

    backuptape_id = Column(Integer, primary_key=True)
    tapedir = Column(String(255), nullable=True)
    nametext = Column(String(255), nullable=True)
    tapedate = Column(DateTime, nullable=True)

    @classmethod
    def exists(cls, tapedir):
        """Check if a tape already exists

        Args:
            tapedir (str): the name of the tape, e.g. tape036_037

        Returns:
            int: backuptape_id on exists
            False: on not exists

        """
        try:
            rs = (cls.query(cls.backuptape_id.label('id'))
                     .filter(cls.tapedir == tapedir).one())
            return rs.id
        except NoResultFound:
            return False


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

        """SELECT major, minor, patch, name FROM version ORDER BY time DESC LIMIT 1"""
        return (cls.query(Version.major.label('major'),
                          Version.minor.label('minor'),
                          Version.patch.label('patch'),
                          Version.name.label('name'))
                   .order_by(Version.time.desc()).limit(1).one())

    @classmethod
    def check(cls, dbname, ver):
        """Checks version of database against dbname and version

        [normally from the config file]

        Args:
          dbname (str): database name as stored in table version
          ver (str): version string in the format major.minor.patch

        Returns:
          True: if identical
        """
        rs = cls.get_version()
        if rs is not None:
            ver_string = "{0}.{1}.{2}".format(str(rs.major), str(rs.minor),
                                              str(rs.patch))
            return ((ver_string == ver) and (dbname == rs.name))
