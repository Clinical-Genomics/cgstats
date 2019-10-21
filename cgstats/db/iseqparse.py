""" code to parse the iseq samplesheet """

from __future__ import print_function, division

import errno
import logging
import os
import socket
import sys
from glob import glob
from pathlib import Path
from sqlalchemy import func

from demux.utils import iseqSampleSheet
from cgstats.db.models import Supportparams, Datasource, Flowcell, Demux, Project, Sample, Unaligned
from cgstats.utils import iseqstats
from cgstats.utils.utils import get_projects, gather_flowcell

LOGGER = logging.getLogger(__name__)


def gather_supportparams(demux_dir, unaligned_dir):
    """Aggregates all the support params:
    - bcl2fastq version
    - bcl2fastq path
    - command executed
    - datetime
    - SampleSheet.csv path
    - SampleSheet
    - DEMUX path

    Args:
        demux_dir (str): FQPN run dir

    Returns: dict(
        'document_path',
        'idstring',
        'program',
        'commandline',
        'sampleconfig_path',
        'sampleconfig',
        'time')
    """
    params = {}  # result set

    # get some info from bcl2 fastq
    demux_dir = Path(demux_dir)
    logfile = demux_dir.joinpath('projectlog.*.log')
    logfilenames = glob(logfile)  # should yield one result
    logfilenames.sort(key=os.path.getmtime, reverse=True)
    if len(logfilenames) == 0:
        LOGGER.error('No log files found! Looking for %s', format(logfile))
        raise IOError(errno.ENOENT, os.strerror(errno.ENOENT), logfile)

    with open(logfilenames[0], 'r') as logfile:
        for line in logfile.readlines():
            if 'bcl2fastq v' in line:
                params['idstring'] = line.strip()

            if '--use-bases-mask' in line:
                line = line.strip()
                split_line = line.split(' ')
                params['commandline'] = ' '.join(split_line[1:])  # remove the leading [date]
                params['time'] = split_line[0].strip('[]')  # remove the brackets around the date
                params['program'] = split_line[1]  # get the executed program
                break

    # get the sample sheet and it's contents
    document_path = demux_dir.joinpath(unaligned_dir)
    samplesheet_path = document_path.joinpath('SampleSheet.csv')
    params['sampleconfig_path'] = str(samplesheet_path)
    params['sampleconfig'] = iseqSampleSheet(samplesheet_path).raw()

    # get the unaligned dir
    if not os.path.isdir(document_path):
        LOGGER.error("Unaligned dir not found at '%s'", format(document_path))
        import errno
        raise IOError(errno.ENOENT, os.strerror(errno.ENOENT), document_path)

    params['document_path'] = str(document_path)
    return params


def gather_datasource(run_dir, unaligned_dir):
    """Gathers the datasource from run_dir and unaligned_dir"""

    run_dir = Path(run_dir)
    datasource = {}  # result set

    # get the run name
    datasource['runname'] = str(run_dir.normpath().basename())

    # get the run date
    datasource['rundate'] = datasource['runname'].split('_')[0]

    # get the machine name
    datasource['machine'] = datasource['runname'].split('_')[1]

    # get the server name on which the demux took place
    datasource['servername'] = socket.gethostname()

    # get the stats file
    document_path = run_dir.joinpath(unaligned_dir, 'Stats/ConversionStats.xml')
    if not document_path.is_file():
        LOGGER.error("Stats file not found at '%s'", document_path)
        raise IOError(errno.ENOENT, os.strerror(errno.ENOENT), document_path)

    datasource['document_path'] = str(document_path)

    return datasource


def gather_demux(run_dir):
    """Gathers demux from the run_dir"""

    demux = {}  # result set

    # get some info from bcl2 fastq
    run_dir = Path(run_dir)
    logfile = run_dir.joinpath('projectlog.*.log')
    logfilenames = glob(logfile)  # should yield one result
    logfilenames.sort(key=os.path.getmtime, reverse=True)
    if len(logfilenames) == 0:
        LOGGER.error('No log files found! Looking for %s', format(logfile))
        raise IOError(errno.ENOENT, os.strerror(errno.ENOENT), logfile)

    with open(logfilenames[0], 'r') as logfile:
        for line in logfile.readlines():

            if '--use-bases-mask' in line:
                line = line.strip()
                split_line = line.split(' ')
                basemask_params_pos = \
                    [i for i, x in enumerate(split_line) if x == '--use-bases-mask'][0]
                demux['basemask'] = split_line[basemask_params_pos + 1]

    return demux


def sanitize_sample(sample):
    """Removes the _nxdual9 index indication
    Removes the B (reprep) or F (reception fail) suffix from the sample name

    Args:
        sample (str): a sample name

    Return (str): a sanitized sample name

    """
    return sample.split('_')[0].rstrip('BF')


def get_sample_sheet(demux_dir, unaligned_dir):
    """Parses a sample sheet csv"""

    sample_sheet = []
    samplesheet_file_name = f"{demux_dir}/{unaligned_dir}/SampleSheet.csv"
    with open(samplesheet_file_name, 'r') as samplesheet_fh:
        lines = [line.strip().split(',') for line in samplesheet_fh.readlines()]
        header = []
        for line in lines:
            # skip headers
            if line[0].startswith('['):
                continue
            if line[0] == 'FCID':
                header = line
                continue
            if not header:
                continue

            entry = dict(zip(header, line))
            sample_sheet.append(entry)

    return sample_sheet


def add(manager, demux_dir, unaligned_dir):
    """ Gathers and adds all data to cgstats.

    params:
        manager (managerAlchamy): a manager object which can be used to query the DB
        demux_dir (str): the demux dir of the run
    returns: true on success!
    """
    # ok, let's process the support params
    supportparams_id = Supportparams.exists(os.path.join(demux_dir, unaligned_dir))
    if not supportparams_id:
        new_supportparams = gather_supportparams(demux_dir, unaligned_dir)
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

    datasource_id = Datasource.exists(
        os.path.join(demux_dir, unaligned_dir, 'Stats/ConversionStats.xml'))
    if not datasource_id:
        new_datasource = gather_datasource(demux_dir, unaligned_dir)
        datasource = Datasource()
        datasource.runname = new_datasource['runname']
        datasource.rundate = new_datasource['rundate']
        datasource.machine = new_datasource['machine']
        datasource.server = new_datasource['servername']
        datasource.document_path = new_datasource['document_path']
        datasource.document_type = 'xml'
        datasource.time = func.now()
        datasource.supportparams_id = supportparams_id

        manager.add(datasource)
        manager.flush()
        datasource_id = datasource.datasource_id

    flowcell_namepos = gather_flowcell(demux_dir)
    flowcell_name = flowcell_namepos['pos'] + flowcell_namepos['name']
    flowcell_id = Flowcell.exists(flowcell_name)
    if not flowcell_id:
        flowcell = Flowcell()
        flowcell.flowcellname = flowcell_name
        flowcell.flowcell_pos = 'A'
        flowcell.hiseqtype = 'iseq'
        flowcell.time = func.now()

        manager.add(flowcell)
        manager.flush()
        flowcell_id = flowcell.flowcell_id

    new_demux = gather_demux(demux_dir)
    demux_id = Demux.exists(flowcell_id, new_demux['basemask'])
    if not demux_id:
        demux = Demux()
        demux.flowcell_id = flowcell_id
        demux.datasource_id = datasource_id
        demux.basemask = new_demux['basemask']
        demux.time = func.now()

        manager.add(demux)
        manager.flush()
        demux_id = demux.demux_id

    project_id_of = {}  # project name: project id
    for project_name in get_projects(demux_dir, unaligned_dir='Unaligned*'):
        project_id = Project.exists(project_name)
        if not project_id:
            project_obj = Project()
            project_obj.projectname = project_name
            project_obj.time = func.now()

            manager.add(project_obj)
            manager.flush()
            project_id = project_obj.project_id

        project_id_of[project_name] = project_id

    sample_sheet = get_sample_sheet(demux_dir, unaligned_dir)
    stats_samples = iseqstats.parse_samples(Path(demux_dir).joinpath(unaligned_dir))
    for sample in sample_sheet:
        barcode = sample['index'] if sample['index2'] == '' else f"{sample['index']}+" \
                                                              f"{sample['index2']}"
        sample_id = Sample.exists(sample['Sample_ID'], barcode)
        if not sample_id:
            sample_obj = Sample()
            sample_obj.project_id = project_id_of[sample['Sample_Project']]
            sample_obj.samplename = sample['Sample_ID']
            sample_obj.limsid = sample['Sample_ID'].split('_')[0]
            sample_obj.barcode = barcode
            sample_obj.time = func.now()

            manager.add(sample_obj)
            manager.flush()
            sample_id = sample_obj.sample_id

        if not Unaligned.exists(sample_id, demux_id, 1):
            unaligned_obj = Unaligned()
            unaligned_obj.sample_id = sample_id
            unaligned_obj.demux_id = demux_id
            unaligned_obj.lane = 1
            stats_sample = stats_samples[1][sample['Sample_ID']]
            unaligned_obj.yield_mb = round(int(stats_sample['pf_yield']) / 1000000, 2)
            unaligned_obj.passed_filter_pct = stats_sample['pf_yield_pc']
            unaligned_obj.readcounts = stats_sample['pf_clusters'] * 2
            unaligned_obj.raw_clusters_per_lane_pct = stats_sample['raw_clusters_pc']
            unaligned_obj.perfect_indexreads_pct = round(
                stats_sample['perfect_barcodes'] / stats_sample['barcodes'] * 100, 5) if \
                stats_sample['barcodes'] else 0
            unaligned_obj.q30_bases_pct = stats_sample['pf_Q30']
            unaligned_obj.mean_quality_score = stats_sample['pf_qscore']
            unaligned_obj.time = func.now()

            manager.add(unaligned_obj)

    manager.flush()
    manager.commit()

    return True


if __name__ == '__main__':
    xadd(sys.argv[1:])
