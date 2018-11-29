# -*- coding: utf-8 -*-
from datetime import datetime
import json

from alchy import ModelBase, make_declarative_base
from sqlalchemy import Column, types, orm, ForeignKey, UniqueConstraint
from sqlalchemy.orm.exc import NoResultFound


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError('Type not serializable')


class JsonModel(ModelBase):

    def to_json(self, pretty=False):
        """Serialize to JSON.

        Handle DateTime objects.
        """
        kwargs = dict(indent=4, sort_keys=True) if pretty else dict()
        return json.dumps(self.to_dict(), default=json_serial, **kwargs)


Model = make_declarative_base(Base=JsonModel)


class Project(Model):

    project_id = Column(types.Integer, primary_key=True)
    projectname = Column(types.String(255), nullable=False)
    comment = Column(types.Text)
    time = Column(types.DateTime, nullable=False)

    samples = orm.relationship('Sample', cascade='all', backref=orm.backref('project'))

    def __repr__(self):
        return (u"{self.__class__.__name__}: {self.project_id}"
                .format(self=self))

    @staticmethod
    def exists(project_name):
        """Checks if the Prohect entry already exists

        Args:
            project_name (str): project name without the Project_ prefix

        Returns:
            int: project_id on exists
            False: on not exists

        """
        try:
            rs = (Project.query
                         .filter_by(projectname=project_name).one())
            return rs.project_id
        except NoResultFound:
            return False


class Sample(Model):

    sample_id = Column(types.Integer, primary_key=True)
    project_id = Column(ForeignKey('project.project_id', ondelete='CASCADE'), nullable=False)
    samplename = Column(types.String(255), nullable=False)
    customerid = Column(types.String(255))
    limsid = Column(types.String(255))
    barcode = Column(types.String(255))
    time = Column(types.DateTime)

    unaligned = orm.relationship('Unaligned', cascade='all, delete-orphan', backref=orm.backref('sample'))

    @property
    def lims_id(self):
        """Parse out the LIMS id from the samplename in demux database."""
        sample_part = self.samplename.split('_')[0]
        sanitized_id = sample_part.rstrip('FB')
        return sanitized_id

    @staticmethod
    def exists(sample_name, barcode):
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
            rs = (Sample.query
                        .filter_by(samplename=sample_name)
                        .filter_by(barcode=barcode).one())
            return rs.sample_id
        except NoResultFound:
            return False


class Unaligned(Model):

    unaligned_id = Column(types.Integer, primary_key=True)
    sample_id = Column(ForeignKey('sample.sample_id', ondelete='CASCADE'), nullable=False)
    demux_id = Column(ForeignKey('demux.demux_id', ondelete='CASCADE'), nullable=False)
    lane = Column(types.Integer)
    yield_mb = Column(types.Integer)
    passed_filter_pct = Column(types.Numeric(10, 5))
    readcounts = Column(types.Integer)
    raw_clusters_per_lane_pct = Column(types.Numeric(10, 5))
    perfect_indexreads_pct = Column(types.Numeric(10, 5))
    q30_bases_pct = Column(types.Numeric(10, 5))
    mean_quality_score = Column(types.Numeric(10, 5))
    time = Column(types.DateTime)

    #demux = orm.relationship('Demux', backref=orm.backref('unaligned'))
    #sample = orm.relationship('Sample', single_parent=True, cascade='all, delete-orphan', passive_deletes=True, backref=orm.backref('unaligned'))

    @staticmethod
    def exists(sample_id, demux_id, lane):
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
            rs = (Unaligned.query
                           .filter_by(sample_id=sample_id)
                           .filter_by(demux_id=demux_id)
                           .filter_by(lane=lane).one())
            return rs.unaligned_id
        except NoResultFound:
            return False


class Supportparams(Model):

    supportparams_id = Column(types.Integer, primary_key=True)
    document_path = Column(types.String(255), nullable=False, unique=True)
    systempid = Column(types.String(255))
    systemos = Column(types.String(255))
    systemperlv = Column(types.String(255))
    systemperlexe = Column(types.String(255))
    idstring = Column(types.String(255))
    program = Column(types.String(255))
    commandline = Column(types.Text)
    sampleconfig_path = Column(types.String(255))
    sampleconfig = Column(types.Text)
    time = Column(types.DateTime)

    def __repr__(self):
        return (u'{self.__class__.__name__}: {self.document_path}'.format(self=self))

    @staticmethod
    def exists(document_path):
        """Checks if the supportparams entry already exists

        Args:
            document_path (str): Full path to the Unaligned directory

        Returns:
            int: supportparams_id on exists
            False: on not exists

        """
        try:
            rs = (Supportparams.query
                               .filter_by(document_path=document_path).one())
            return rs.supportparams_id
        except NoResultFound:
            return False


class Datasource(Model):

    datasource_id = Column(types.Integer, primary_key=True)
    supportparams_id = Column(ForeignKey('supportparams.supportparams_id', ondelete='CASCADE'),
                              nullable=False)
    runname = Column(types.String(255))
    machine = Column(types.String(255))
    rundate = Column(types.Date)
    document_path = Column(types.String(255), nullable=False)
    document_type = Column(types.Enum('html', 'xml', 'undefined'),
                           nullable=False, default='html')
    server = Column(types.String(255))
    time = Column(types.DateTime)

    supportparams = orm.relationship('Supportparams', cascade='all',
                                     backref=orm.backref('datasources'))

    def __repr__(self):
        return (u'{self.__class__.__name__}: {self.runname}'.format(self=self))

    @staticmethod
    def exists(document_path):
        """Checks if the Datasource entry already exists

        Args:
            document_path (str): Full path to the stats file

        Returns:
            int: datasource_id on exists
            False: on not exists

        """
        try:
            rs = (Datasource.query
                            .filter_by(document_path=document_path).one())
            return rs.datasource_id
        except NoResultFound:
            return False


class Demux(Model):

    __table_args__ = (UniqueConstraint('flowcell_id', 'basemask',
                                       name='demux_ibuk_1'),)

    demux_id = Column(types.Integer, primary_key=True)
    flowcell_id = Column(ForeignKey('flowcell.flowcell_id', ondelete='CASCADE'), nullable=False)
    datasource_id = Column(ForeignKey('datasource.datasource_id', ondelete='CASCADE'), nullable=False)
    basemask = Column(types.String(255))
    time = Column(types.DateTime)

    datasource = orm.relationship('Datasource', cascade='all', backref=orm.backref('demuxes'))
    unaligned = orm.relation('Unaligned', single_parent=True, cascade='all, delete-orphan', backref=orm.backref('demux'))
    # add the viewonly attribute to make sure the Session.delete(demux) works
    samples = orm.relation('Sample', secondary='unaligned', viewonly=True, cascade='all', backref=orm.backref('demuxes'))

    @staticmethod
    def exists(flowcell_id, basemask):
        """Checks if the Demux entry already exists

        Args:
            flowcell_id (int): flowcell_id in the table Flowcell
            basemask (str): the basemask used to demux, e.g. Y101,I6n,Y101

        Returns:
        int: demux_id on exists
            False: on not exists

        """
        try:
            rs = (Demux.query
                       .filter_by(flowcell_id=flowcell_id)
                       .filter_by(basemask=basemask).one())
            return rs.demux_id
        except NoResultFound:
            return False


class Flowcell(Model):

    flowcell_id = Column(types.Integer, primary_key=True)
    flowcellname = Column(types.String(255), nullable=False, unique=True)
    flowcell_pos = Column(types.Enum('A', 'B'), nullable=False)
    hiseqtype = Column(types.String(255), nullable=False)
    time = Column(types.DateTime)

    demux = orm.relationship('Demux', cascade='all', backref=orm.backref('flowcell'))

    @staticmethod
    def exists(flowcell_name):
        """Checks if the Flowcell entry already exists

        Args:
            flowcell_name (str): The name of the flowcell

        Returns:
            int: flowcell_id on exists
            False: on not exists

        """
        try:
            rs = Flowcell.query.filter_by(flowcellname=flowcell_name).one()
            return rs.flowcell_id
        except NoResultFound:
            return False


class Backup(Model):

    runname = Column(types.String(255), primary_key=True)
    startdate = Column(types.Date, nullable=False)
    nas = Column(types.String(255))
    nasdir = Column(types.String(255))
    starttonas = Column(types.DateTime)
    endtonas = Column(types.DateTime)
    preproc = Column(types.String(255))
    preprocdir = Column(types.String(255))
    startpreproc = Column(types.DateTime)
    endpreproc = Column(types.DateTime)
    frompreproc = Column(types.DateTime)
    analysis = Column(types.String(255))
    analysisdir = Column(types.String(255))
    toanalysis = Column(types.DateTime)
    fromanalysis = Column(types.DateTime)
    inbackupdir = Column(types.Integer)
    backuptape_id = Column(ForeignKey('backuptape.backuptape_id'), nullable=False)
    backupdone = Column(types.DateTime)
    md5done = Column(types.DateTime)

    tape = orm.relationship('Backuptape', backref=orm.backref('backup'))

    @staticmethod
    def exists(runname, tapedir=None):
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
                rs = (Backup.query
                            .outerjoin(Backuptape)
                            .filter_by(runname=runname)
                            .filter(Backuptape.tapedir == tapedir).one())
            else:
                rs = Backup.query.filter_by(runname=runname).one()
            return rs.runname
        except NoResultFound:
            return False


class Backuptape(Model):

    backuptape_id = Column(types.Integer, primary_key=True)
    tapedir = Column(types.String(255))
    nametext = Column(types.String(255))
    tapedate = Column(types.DateTime)

    @staticmethod
    def exists(tapedir):
        """Check if a tape already exists

        Args:
            tapedir (str): the name of the tape, e.g. tape036_037

        Returns:
            int: backuptape_id on exists
            False: on not exists

        """
        try:
            rs = Backuptape.query.filter_by(tapedir=tapedir).one()
            return rs.backuptape_id
        except NoResultFound:
            return False


class Version(Model):

    __table_args__ = (UniqueConstraint('name', 'major', 'minor', 'patch',
                                       name='name_major_minor_patch_uc'),)

    version_id = Column(types.Integer, primary_key=True)
    name = Column(types.String(255))
    major = Column(types.Integer)
    minor = Column(types.Integer)
    patch = Column(types.Integer)
    comment = Column(types.String(255))
    time = Column(types.DateTime, nullable=False)

    @staticmethod
    def get_version():
        """Retrieves the database version

        Returns (tuple): (major, minor, patch, name)
        """

        """SELECT major, minor, patch, name FROM version ORDER BY time DESC LIMIT 1"""
        return Version.query.order_by(Version.time.desc()).limit(1).one()

    @staticmethod
    def check(dbname, ver):
        """Checks version of database against dbname and version

        [normally from the config file]

        Args:
          dbname (str): database name as stored in table version
          ver (str): version string in the format major.minor.patch

        Returns:
          True: if identical
        """
        rs = Version.get_version()
        if rs is not None:
            ver_string = "{0}.{1}.{2}".format(str(rs.major), str(rs.minor),
                                              str(rs.patch))
            return ((ver_string == ver) and (dbname == rs.name))
