#!/usr/bin/env python
# -*- coding: utf-8 -*-

from path import Path

from cgstats.utils.utils import gather_flowcell
from cgstats.db import parse
from cgstats.db import xparse
from cgstats.db.models import Flowcell, Sample, Demux, Unaligned, Datasource, Supportparams, Project
from cgstats.db import api

wgs_sample_count = 8
wes_sample_count = 7
wes8_sample_count = 10
wes9_sample_count = 8
wgs_lane_count = 8
wes_lane_count = 2

def test_db_add(sql_manager, rapid_run_dir, x_run_dir):
    """ Add a rapid flowcell. We know the rowcounts for all tables.
    Add an X flowcell to add some more data.

    * do we get the right amount of counts for all tables?
    * check the presence of a randomly chosen sample.
    * add the flowcells again. Duplicates?
    """

    def _count_all_tables():
        # ok, do we have the right counts ...
        samples = Sample.query.all()
        projects = Project.query.all()
        flowcells = Flowcell.query.all()
        demuxes = Demux.query.all()
        unaligneds = Unaligned.query.all()
        datasources = Datasource.query.all()
        supportparams = Supportparams.query.all()
        assert len(samples) == wgs_sample_count + wes_sample_count
        assert len(projects) == 4
        assert len(flowcells) == 2
        assert len(demuxes) == 2

        # unaligned will have one row for each sample and for each lane it was run on
        assert len(unaligneds) == wgs_sample_count + wes_sample_count * wes_lane_count
        assert len(datasources) == 2
        assert len(supportparams) == 2

    unaligned = 'Unaligned'
    parse.add(sql_manager, rapid_run_dir, unaligned)
    xparse.add(sql_manager, x_run_dir) # adds 8 wgs samples

    # let's just quickly check if the added information is correct
    samples = Sample.query.filter_by(limsid='SIB914A11').all()
    assert len(samples) == 1
    sample = samples.pop()
    assert sample.limsid == 'SIB914A11'
    assert sample.samplename == 'SIB914A11_sureselect11'

    _count_all_tables()

    # let's add it again and check if we have duplicates
    parse.add(sql_manager, rapid_run_dir, unaligned)
    xparse.add(sql_manager, x_run_dir)
    samples = Sample.query.filter_by(limsid='SIB914A11').all()
    assert len(samples) == 1

    _count_all_tables()


def test_select(sql_manager, rapid_run_dir, x_run_dir):
    """ Tests out one query that touches a lot of the tables.
    Do we get the expected result? """

    flowcell = gather_flowcell(rapid_run_dir)['name']
    project = '504910'
    unaligned = 'Unaligned'
    xparse.add(sql_manager, x_run_dir)
    parse.add(sql_manager, rapid_run_dir, unaligned)
    selection = api.select(flowcell, project).all()

    assert selection == [
        ('SIB914A11_sureselect11', 'HB07NADXX', '1,2', '38088672,38269896', 76358568, '3847,3865', 7712, '93.71,93.70', '36.27,36.27'),
        ('SIB914A12_sureselect12', 'HB07NADXX', '1,2', '48201748,48191852', 96393600, '4868,4867', 9735, '94.39,94.40', '36.49,36.49'),
        ('SIB914A15_sureselect15', 'HB07NADXX', '1,2', '57947620,57997530', 115945150, '5853,5858', 11711, '94.32,94.33', '36.46,36.46'),
        ('SIB914A2_sureselect2',   'HB07NADXX', '1,2', '32032000,32016648', 64048648, '3235,3234', 6469, '94.11,94.12', '36.40,36.40')
    ]

def test_db_delete_sample(sql_manager, rapid_run_dir, x_run_dir):
    """ Add a rapid and a X flowcell. Delete a rapid sample.

    * Expected: one Sample less. Two Unaligned rows less.
    """
    unaligned = 'Unaligned'

    xparse.add(sql_manager, x_run_dir) # adds 8 wgs samples
    parse.add(sql_manager, rapid_run_dir, unaligned) # adds 7 WES samples all run on two lanes

    # make sure the sample is there to start with
    sample = Sample.query.filter(Sample.limsid == 'SIB914A11').all()
    assert len(sample) == 1

    # let's try to delete a sample
    sql_manager.delete(sample)
    sql_manager.commit()

    # ok, do we have the right counts ...
    sample = Sample.query.filter(Sample.limsid == 'SIB914A11').all()
    samples = Sample.query.all()
    flowcells = Flowcell.query.all()
    demuxes = Demux.query.all()
    unaligneds = Unaligned.query.all()
    datasources = Datasource.query.all()
    assert len(sample) == 0

    # one sample is removed
    assert len(samples) == wes_sample_count + wgs_sample_count - 1

    # one sample removed from the rapid run, means 2 unaligned rows removed
    assert len(unaligneds) == wes_sample_count * wes_lane_count + wgs_sample_count - 2

    assert len(flowcells) == 2
    assert len(demuxes) == 2
    assert len(datasources) == 2

def test_db_delete_demux(sql_manager, rapid_run_dir, x_run_dir, mixed_rapid_run_dir):
    """ Add a rapid and an X flowcell. Delete the demux row of the rapid.
    This should remove all rows from all tables related to the rapid flowcell.
    """
    unaligned = 'Unaligned'

    xparse.add(sql_manager, x_run_dir)
    parse.add(sql_manager, rapid_run_dir, unaligned)

    # is the demux there?
    demux = Demux.query.filter(Demux.basemask == 'Y101,I6n,Y101').all()
    assert len(demux) == 1

    # let's try to delete a demux
    sql_manager.delete(demux)
    sql_manager.commit()

    # ok, do we have the counts ...
    demux = Demux.query.all()
    unaligneds = Unaligned.query.join(Sample).all()
    samples = Sample.query.all()
    flowcells = Flowcell.query.all()
    datasources = Datasource.query.all()
    supportparams = Supportparams.query.all()
    assert len(demux) == 1
    assert len(unaligneds) == wgs_sample_count
    assert len(samples) == wgs_sample_count
    assert len(flowcells) == 2 # does not automatically delete FC when it's an orphan
    assert len(datasources) == 1
    assert len(supportparams) == 1

    # now the most important test: add a variable length index rapid FC and remove one demux
    parse.add(sql_manager, mixed_rapid_run_dir, 'Unaligned8', 'SampleSheet8.csv')
    parse.add(sql_manager, mixed_rapid_run_dir, 'Unaligned9', 'SampleSheet9.csv')

    # are the demuxes there?
    demux8 = Demux.query.filter(Demux.basemask == 'Y126,I8,I8,Y126').all()
    demux9 = Demux.query.filter(Demux.basemask == 'Y126,I8,n8,Y126').all()
    assert len(demux8) == 1
    assert len(demux9) == 1

    # let's remove one demux
    sql_manager.delete(demux8)
    sql_manager.commit()

    # ok, do we have the counts ...
    demux = Demux.query.all()
    unaligneds = Unaligned.query.join(Sample).all()
    samples = Sample.query.all()
    flowcells = Flowcell.query.all()
    datasources = Datasource.query.all()
    supportparams = Supportparams.query.all()
    assert len(demux) == 2
    assert len(unaligneds) == wgs_sample_count + wes9_sample_count * wes_lane_count
    assert len(samples) == wgs_sample_count + wes9_sample_count
    assert len(flowcells) == 3
    assert len(datasources) == 2
    assert len(supportparams) == 2


def test_db_delete_flowcell(sql_manager, rapid_run_dir, x_run_dir, x_pooled_run_dir):
    """ Add a rapid and a X flowclel. Delete the X flowcell.
    This should remove all rows from all tables related to the rapid flowcell."""
    unaligned = 'Unaligned'
    flowcell_name = gather_flowcell(x_run_dir)['name']

    # let's try to delete a flowcell
    xparse.add(sql_manager, x_run_dir)
    parse.add(sql_manager, rapid_run_dir, unaligned)

    # is the flowcell there?
    flowcell = Flowcell.query.filter(Flowcell.flowcellname == flowcell_name).all()
    assert len(flowcell) == 1

    # let's try to delete a demux
    sql_manager.delete(flowcell)
    sql_manager.commit()

    # ok, do we have the counts ...
    flowcells = Flowcell.query.all()
    unaligneds = Unaligned.query.join(Sample).all()
    samples = Sample.query.all()
    demux = Demux.query.all()
    datasources = Datasource.query.all()
    supportparams = Supportparams.query.all()
    assert len(demux) == 1
    assert len(unaligneds) == wes_sample_count * wes_lane_count
    assert len(samples) == wes_sample_count
    assert len(flowcells) == 1
    assert len(datasources) == 1
    assert len(supportparams) == 1
