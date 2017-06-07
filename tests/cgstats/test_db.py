#!/usr/bin/env python
# -*- coding: utf-8 -*-

from path import Path

from cgstats.db import parse
from cgstats.db import xparse
from cgstats.db.models import Flowcell, Sample, Demux, Unaligned, Datasource
from cgstats.db import api

def test_db_add(sql_manager, rapid_run_dir):
    unaligned = 'Unaligned'
    flowcell = 'HB07NADXX'
    parse.add(sql_manager, rapid_run_dir, unaligned)

    samples = Sample.query.filter_by(limsid='SIB914A11').all()

    assert len(samples) == 1
    sample = samples.pop()
    assert sample.limsid == 'SIB914A11'
    assert sample.samplename == 'SIB914A11_sureselect11'

def test_select(sql_manager, rapid_run_dir):
    flowcell = 'HB07NADXX'
    project = '504910'
    unaligned = 'Unaligned'
    parse.add(sql_manager, rapid_run_dir, unaligned)
    selection = api.select(flowcell, project).all()

    assert selection == [
        ('SIB914A11_sureselect11', 'HB07NADXX', '1,2', '38088672,38269896', 76358568, '3847,3865', 7712, '93.71,93.70', '36.27,36.27'),
        ('SIB914A12_sureselect12', 'HB07NADXX', '1,2', '48201748,48191852', 96393600, '4868,4867', 9735, '94.39,94.40', '36.49,36.49'),
        ('SIB914A15_sureselect15', 'HB07NADXX', '1,2', '57947620,57997530', 115945150, '5853,5858', 11711, '94.32,94.33', '36.46,36.46'),
        ('SIB914A2_sureselect2', 'HB07NADXX', '1,2', '32032000,32016648', 64048648, '3235,3234', 6469, '94.11,94.12', '36.40,36.40')
    ]

def test_db_add_remove(sql_manager, rapid_run_dir, x_run_dir, x_pooled_run_dir):
    unaligned = 'Unaligned'
    flowcell = 'HB07NADXX'
    parse.add(sql_manager, rapid_run_dir, unaligned)
    #xparse.add(sql_manager, x_pooled_run_dir)
    xparse.add(sql_manager, x_run_dir) # adds 8 samples

    # let's try to delete a sample
    sample = Sample.query.filter(Sample.limsid == 'SIB914A11').all()
    assert len(sample) == 1

    sql_manager.delete(sample)
    sql_manager.commit()

    sample = Sample.query.filter(Sample.limsid == 'SIB914A11').all()
    assert len(sample) == 0

    # let's try to delete a demux
    demux = Demux.query.filter(Demux.basemask == 'Y101,I6n,Y101').all()
    assert len(demux) == 1

    sql_manager.delete(demux)
    sql_manager.commit()

    demux = Demux.query.filter(Demux.basemask == 'Y101,I6n,Y101').all()
    unaligneds = Unaligned.query.join(Sample).all()
    samples = Sample.query.all()
    flowcells = Flowcell.query.filter(Flowcell.flowcellname == flowcell).all()
    datasources = Datasource.query.filter(Datasource.runname == Path(rapid_run_dir).basename()).all()
    assert len(demux) == 0
    assert len(unaligneds) == 8
    assert len(samples) == 8
    assert len(flowcells) == 0
    assert len(datasources) == 0

    # let's try to delete a flowcell




