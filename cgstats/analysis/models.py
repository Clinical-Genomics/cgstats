# -*- coding: utf-8 -*-
import json

from sqlalchemy import Column, types, orm, ForeignKey

from cgstats.db import Model


class SampleFlowcell(Model):

    """Represent a single flowcell for a sample."""

    id = Column(types.Integer, primary_key=True)
    flowcell_id = Column(types.String(16))
    sample_id = Column(ForeignKey('analysis_sample.id'))

    lane = Column(types.Integer)
    cbot_machine = Column(types.String(32))
    sequencing_machine = Column(types.String(32))
    sequencing_date = Column(types.DateTime)
    run_mode = Column(types.String(32))
    sequencing_reagents_1 = Column(types.String(32))
    sequencing_reagents_2 = Column(types.String(32))
    sequencing_cluster_1 = Column(types.String(32))
    sequencing_cluster_2 = Column(types.String(32))
    cluster_concentration = Column(types.Float)
    q30 = Column(types.Float)
    reads = Column(types.Integer)


class AnalysisSample(Model):

    """Sample level QC metrics from an anlaysis."""

    id = Column(types.Integer, primary_key=True)
    sample_id = Column(types.String(32), unique=True)
    analysis_id = Column(ForeignKey('analysis.id'))
    sequencing_type = Column(types.Enum('wes', 'wgs'))
    sex_predicted = Column(types.Enum('male', 'female', 'unknown'))

    # pre-sequencing lab stuff
    capture_kit = Column(types.String(32))
    library_kit_lot_1 = Column(types.String(32))
    library_kit_lot_2 = Column(types.String(32))
    # can sometimes be a mix of two kits
    baits_lot = Column(types.String(64))
    beads_t1_lot = Column(types.String(32))
    fragment_size = Column(types.Integer)
    dna_concentration = Column(types.Float)
    input_material = Column(types.Float)
    index_sequence = Column(types.String(32))

    # mapping/alignment
    reads_total = Column(types.Integer)
    mapped_percent = Column(types.Float)
    duplicates_percent = Column(types.Float)
    strand_balance = Column(types.Float)

    # coverage
    coverage_target = Column(types.Float)
    completeness_target_10 = Column(types.Float)
    completeness_target_20 = Column(types.Float)
    completeness_target_50 = Column(types.Float)
    completeness_target_100 = Column(types.Float)

    # OMIM stats
    # 10-100X completeness

    # variant calling
    variants = Column(types.Integer)  # WHERE?
    indels = Column(types.Integer)
    snps = Column(types.Integer)
    novel_sites = Column(types.Integer)  # WHERE?
    concordant_rate = Column(types.Float)
    hethom_ratio = Column(types.Float)
    titv_ratio = Column(types.Float)

    flowcells = orm.relationship('SampleFlowcell', cascade='all,delete',
                                 backref='sample')

    @property
    def read_pairs(self):
        return self.reads_total / 2


class Analysis(Model):

    """Meta-data class to group samples from the same analysis."""

    id = Column(types.Integer, primary_key=True)
    # composed from "{customer_id}-{name}"
    analysis_id = Column(types.String(64), unique=True)
    pipeline = Column(types.String(32))
    pipeline_version = Column(types.String(32))
    analyzed_at = Column(types.DateTime)
    _program_versions = Column(types.Text)

    @property
    def program_versions(self):
        return json.loads(self._program_versions) if self._program_versions else {}

    @program_versions.setter
    def program_versions(self, value):
        self._program_versions = json.dumps(value)

    samples = orm.relationship('AnalysisSample', cascade='all,delete',
                               backref='analysis')

    @property
    def family_id(self):
        return self.analysis_id.split('-', 1)[-1]
