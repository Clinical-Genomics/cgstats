#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function, division

import sys
import os
import glob
import time
import re
import socket
import ast
from datetime import datetime

from sqlalchemy import func
from path import Path

from demux.utils import HiSeq2500Samplesheet
from cgstats.utils import stats as hiseqstats
from cgstats.utils.utils import get_projects, gather_flowcell
from cgstats.db.models import Supportparams, Version, Datasource, Flowcell, Demux, Project, Sample, Unaligned

def gather_supportparams(demuxdir, unaligneddir):
    """
    """
    support_file = demuxdir.joinpath(unaligneddir, 'support.txt')

    system_str = ""
    command_str = ""
    idstring = ""
    program = ""

    lines = (line.strip() for line in open(support_file))
    for line in lines:
        if line.startswith('$_System'):
            line = line.replace('$_System = ', '')
            system_str += line + '\n'
            continue

        if system_str:
            if line.startswith("};"):
                system_str += '}'
                break
            else:
                system_str += line + '\n'

    system = ast.literal_eval(system_str)

    for line in lines:
        if line.startswith('$_ID-string'):
            idstring = line.replace("$_ID-string = '","")
            idstring = idstring.replace("';","")
        if line.startswith('$_Program'):
            program = line.replace("$_Program = '","")
            program = program.replace("';","")
            break

    for line in lines:
        if line.startswith('$_Command-line'):
            line = line.replace('$_Command-line = ', '')
            command_str += line + '\n'
            continue

        if command_str:
            if line.startswith("];"):
                command_str += ']'
                break
            else:
                command_str += line + '\n'

    c = ast.literal_eval(command_str)

    command = {
        '--sample-sheet': c[ c.index('--sample-sheet') + 1],
        '--use-bases-mask': c[ c.index('--use-bases-mask') + 1],
    }

    samplesheet_path = str(demuxdir.joinpath('SampleSheet.csv'))
    samplesheet = HiSeq2500Samplesheet(samplesheet_path)

    return {
        'system': system,
        'command': command,
        'program': program,
        'idstring': idstring,
        'document_path': str(support_file),
        'commandline': ' '.join([ program, ' '.join(c)]),
        'sampleconfig_path': samplesheet_path,
        'sampleconfig': samplesheet.raw(),
        'time': datetime.fromtimestamp(support_file.getmtime())
    }

def gather_datasource(demuxdir):
    rs = {} # resultset

    runname = demuxdir.normpath().basename()
    name_parts = runname.split("_")

    rs['runname'] = str(runname)
    rs['rundate'] = name_parts[0]
    rs['machine'] = name_parts[1]
    rs['servername'] = socket.gethostname()

    return rs

def get_basemask(supportparams):
    return supportparams['command']['--use-bases-mask']

def add(manager, demux_dir, unaligned_dir):
    """TODO: Docstring for add.
    Returns: TODO

    """

    demux_dir = Path(demux_dir)
    demux_stats = glob.glob(demux_dir.joinpath(unaligned_dir, 'Basecall_Stats_*', 'Demultiplex_Stats.htm'))[0]

    samplesheet_path = demux_dir.joinpath('SampleSheet.csv')
    samplesheet = Samplesheet(samplesheet_path)

    stats = hiseqstats.parse(demux_stats)

    supportparams_id = Supportparams.exists(demux_dir.joinpath(unaligned_dir))
    new_supportparams = gather_supportparams(demux_dir, unaligned_dir)
    if not supportparams_id:
        supportparams = Supportparams()
        supportparams.document_path = new_supportparams['document_path']
        supportparams.idstring = new_supportparams['idstring']
        supportparams.program = new_supportparams['program']
        supportparams.commandline = new_supportparams['commandline']
        supportparams.sampleconfig_path = new_supportparams['sampleconfig_path']
        supportparams.sampleconfig = new_supportparams['sampleconfig']
        supportparams.time = new_supportparams['time']

        manager.add(supportparams)
        manager.flush()
        supportparams_id = supportparams.supportparams_id

    datasource_id = Datasource.exists(str(demux_stats))
    if not datasource_id:
        new_datasource = gather_datasource(demux_dir)
        datasource = Datasource()
        datasource.runname = new_datasource['runname']
        datasource.rundate = new_datasource['rundate']
        datasource.machine = new_datasource['machine']
        datasource.server = new_datasource['servername']
        datasource.document_path = str(demux_stats)
        datasource.document_type = 'html'
        datasource.time = func.now()
        datasource.supportparams_id = supportparams_id

        manager.add(datasource)
        manager.flush()
        datasource_id = datasource.datasource_id

    flowcell_namepos = gather_flowcell(demux_dir)
    flowcell_name = flowcell_namepos['name']
    flowcell_pos  = flowcell_namepos['pos']
    flowcell_id   = Flowcell.exists(flowcell_name)
    if not flowcell_id:
        flowcell = Flowcell()
        flowcell.flowcellname = flowcell_name
        flowcell.flowcell_pos = flowcell_pos
        flowcell.hiseqtype = 'hiseqga'
        flowcell.time = func.now()

        manager.add(flowcell)
        manager.flush()
        flowcell_id = flowcell.flowcell_id

    basemask = get_basemask(new_supportparams)
    demux_id = Demux.exists(flowcell_id, basemask)
    if not demux_id:
        demux = Demux()
        demux.flowcell_id = flowcell_id
        demux.datasource_id = datasource_id
        demux.basemask = basemask
        demux.time = func.now()

        manager.add(demux)
        manager.flush()
        demux_id = demux.demux_id

    project_id_of = {} # project name: project id
    for project_name in get_projects(demux_dir, unaligned_dir):
        project_id = Project.exists(project_name)
        if not project_id:
            p = Project()
            p.projectname = project_name
            p.time = func.now()

            manager.add(p)
            manager.flush()
            project_id = p.project_id

        project_id_of[ project_name ] = project_id

    for line in samplesheet.lines():
        sample_id = Sample.exists(samplesheet.cell(line, 'sample_id'), line['Index'])
        if not sample_id:
            s = Sample()
            s.project_id = project_id_of[ line['SampleProject'] ]
            s.samplename = line['SampleID']
            s.limsid = line['SampleID'].split('_')[0]
            s.barcode = line['Index']
            s.time = func.now()

            manager.add(s)
            manager.flush()
            sample_id = s.sample_id

        if not Unaligned.exists(sample_id, demux_id, line['Lane']):
            u = Unaligned()
            u.sample_id = sample_id
            u.demux_id = demux_id
            u.lane = line['Lane']
            stats_sample = stats[line['Lane']][line['SampleID']]

            u.yield_mb = int(stats_sample['yield_mb'])
            u.passed_filter_pct = stats_sample['pf_pc']
            u.readcounts = stats_sample['readcounts']
            u.raw_clusters_per_lane_pct = stats_sample['raw_clusters_pc']
            u.perfect_indexreads_pct = stats_sample['perfect_barcodes_pc']
            u.q30_bases_pct = stats_sample['q30_bases_pc']
            u.mean_quality_score = stats_sample['mean_quality_score']
            u.time = func.now()

            manager.add(u)

    manager.flush()
    manager.commit()

    return True

    #""" Set up data for table datasource """
    #
    #servername = socket.gethostname()
    #getdatasquery = """ SELECT datasource_id FROM datasource WHERE document_path = '""" + demultistats + """' """
    #indbdatas = dbc.generalquery(getdatasquery)
    #if not indbdatas:
    #  insertdict = { 'document_path': demultistats, 'runname': runname, 'rundate': rundate, 'machine': machine, 
    #                 'supportparams_id': supportparamsid, 'server': servername, 'time': now }
    #  outcome = dbc.sqlinsert('datasource', insertdict)
    #  datasourceid = outcome['datasource_id']
    #else:
    #  datasourceid = indbdatas[0]['datasource_id']
  
    #""" Set up data for table flowcell """
  
    #getflowcellquery = """ SELECT flowcell_id FROM flowcell WHERE flowcellname = '""" + fc + """' """
    #indbfc = dbc.generalquery(getflowcellquery)
    #if not indbfc:
    #  insertdict = { 'flowcellname': fc, 'flowcell_pos': Flowcellpos, 'time': now }
    #  outcome = dbc.sqlinsert('flowcell', insertdict)
    #  flowcellid = outcome['flowcell_id']
    #else:
    #  flowcellid = indbfc[0]['flowcell_id']
  
    #""" Set up data for table demux """
    #
    #getdemuxquery = """ SELECT demux_id FROM demux WHERE flowcell_id = '""" + str(flowcellid) + """' 
    #                    AND basemask = '""" + bmask + """' """
    #indbdemux = dbc.generalquery(getdemuxquery)
    #if not indbdemux:
    #  insertdict = { 'flowcell_id': flowcellid, 'datasource_id': datasourceid, 'basemask': bmask, 'time': now }
    #  outcome = dbc.sqlinsert('demux', insertdict)
    #  demuxid = outcome['demux_id']
    #else:
    #  demuxid = indbdemux[0]['demux_id']
  
    #""" Set up data for table project """
  
    #projects = {}
    #tables = soup.findAll("table")
    #rows = tables[1].findAll('tr')
    #for row in rows:
    #  cols = row.findAll('td')
    #  project = unicode(cols[6].string).encode('utf8')
    #  getprojquery = """ SELECT project_id, time FROM project WHERE projectname = '""" + project + """' """
    #  indbproj = dbc.generalquery(getprojquery)
    #  if not indbproj:
    #    insertdict = { 'projectname': project, 'time': now }
    #    outcome = dbc.sqlinsert('project', insertdict)
    #    projects[project] = outcome['project_id']
    #  else:
    #    projects[project] = indbproj[0]['project_id']
  
    #""" Set up data for table sample """
  
    #samples = {}
    #for row in rows:
    #  cols = row.findAll('td')
    #  samplename = unicode(cols[1].string).encode('utf8')
    #  limsid = samplename.split('_')[0]
    #  barcode = unicode(cols[3].string).encode('utf8')
    #  project = unicode(cols[6].string).encode('utf8')
    #  getsamplequery = """ SELECT sample_id FROM sample WHERE samplename = '""" + samplename + """' 
    #                       AND barcode = '""" + barcode + """' """
    #  indbsample = dbc.generalquery(getsamplequery)
    #  if not indbsample:
    #    insertdict = { 'samplename': samplename, 'limsid': limsid, 'project_id': projects[project], 'barcode': barcode, 'time': now }
    #    outcome = dbc.sqlinsert('sample', insertdict)
    #    samples[samplename] = outcome['sample_id']
    #  else:
    #    samples[samplename] = indbsample[0]['sample_id']
  
    #""" Set up data for table unaligned """
  
    #for row in rows:
    #  cols = row.findAll('td')
    #  lane = unicode(cols[0].string).encode('utf8')
    #  samplename = unicode(cols[1].string).encode('utf8')
    #  barcode = unicode(cols[3].string).encode('utf8')
    #  project = unicode(cols[6].string).encode('utf8')
    #  yield_mb = unicode(cols[7].string).encode('utf8')
    #  yield_mb = yield_mb.replace(",","")
    #  passed_filter_pct = unicode(cols[8].string).encode('utf8')
    #  Readcounts = unicode(cols[9].string).encode('utf8')
    #  Readcounts = Readcounts.replace(",","")
    #  raw_clusters_per_lane_pct = unicode(cols[10].string).encode('utf8')
    #  perfect_indexreads_pct = unicode(cols[11].string).encode('utf8')
    #  q30_bases_pct = unicode(cols[13].string).encode('utf8')
    #  mean_quality_score = unicode(cols[14].string).encode('utf8')
  
    #  getunalquery = """ SELECT unaligned_id FROM unaligned WHERE sample_id = '""" + str(samples[samplename]) + """' 
    #                     AND lane = '""" + lane + """' AND demux_id = '""" + str(demuxid) + """' """
    #  indbunal = dbc.generalquery(getunalquery)
    #  if not indbunal:
    #    insertdict = { 'sample_id': samples[samplename], 'demux_id': str(demuxid), 'lane': lane, 
    #                   'yield_mb': yield_mb, 'passed_filter_pct': passed_filter_pct, 'readcounts': Readcounts, 
    #                    'raw_clusters_per_lane_pct': raw_clusters_per_lane_pct, 
    #                    'perfect_indexreads_pct': perfect_indexreads_pct, 'q30_bases_pct': q30_bases_pct, 
    #                    'mean_quality_score': mean_quality_score, 'time': now }
    #    outcome = dbc.sqlinsert('unaligned', insertdict)
    #    unalignedid = outcome['unaligned_id']
    #  else:
    #    unalignedid = indbunal[0]['unaligned_id']
