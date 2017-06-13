#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function, division

import xml.etree.cElementTree as et
import glob
import re
import os

from path import Path

from demux.utils import Samplesheet

def xpathsum(tree, xpath):
    """Sums all numbers found at these xpath nodes

    Args:
        tree (an elementTree): parsed XML as an elementTree
        xpath (str): an xpath the XML nodes

    Returns (int): the sum of all nodes

    """
    numbers = tree.findall(xpath)
    return sum(( int(number.text) for number in numbers ))

def get_barcode_summary(tree, project, sample, barcode):
    """Calculates following statistics from the DemultiplexingStats file
    * BarcodeCount
    * PerfectBarcodeCount
    * OneMismatchBarcodeCount

    Args:
        tree (an elementTree): parsed XML as an elementTree

    Returns: TODO

    """
    barcodes = xpathsum(tree, "Flowcell/Project[@name='{project}']/Sample[@name='{sample}']/Barcode[@name='{barcode}']/Lane/BarcodeCount".format(project=project, sample=sample, barcode=barcode))
    perfect_barcodes = xpathsum(tree, "Flowcell/Project[@name='{project}']/Sample[@name='{sample}']/Barcode[@name='{barcode}']/Lane/PerfectBarcodeCount".format(project=project, sample=sample, barcode=barcode))
    one_mismatch_barcodes = xpathsum(tree, "Flowcell/Project[@name='{project}']/Sample[@name='{sample}']/Barcode[@name='{barcode}']/Lane/OneMismatchBarcodeCount".format(project=project, sample=sample, barcode=barcode))

    return {
        'barcodes': barcodes,
        'perfect_barcodes': perfect_barcodes,
        'one_mismatch_barcodes': one_mismatch_barcodes,
    }

def get_sample_summary( tree, project, sample, barcode):
    """Calculates following statistics from from the ConversionStats file, for a sample
    * pf clusters
    * pf yield
    * pf Q30
    * raw Q30
    * pf Q Score

    Args:
        tree (an elementTree): parsed XML as an elementTree
        project (str): A project name
        sample (str): A sample name. In our case, this is the same as the project
        barcode (str): An index identifying a sample

    Returns (dict): with following keys: pf_clusters, pf_yield, pf_q30, pf_read1_yield, pf_read2_yield, pf_read1_q30, pf_read2_q30, pf_qscore_sum, pf_qscore

    """
    raw_clusters = xpathsum(tree, "Flowcell/Project[@name='{project}']/Sample[@name='{sample}']/Barcode[@name='{barcode}']/Lane/Tile/Raw/ClusterCount".format(project=project, sample=sample, barcode=barcode))
    pf_clusters = xpathsum(tree, "Flowcell/Project[@name='{project}']/Sample[@name='{sample}']/Barcode[@name='{barcode}']/Lane/Tile/Pf/ClusterCount".format(project=project, sample=sample, barcode=barcode))

    pf_yield = xpathsum(tree, "Flowcell/Project[@name='{project}']/Sample[@name='{sample}']/Barcode[@name='{barcode}']/Lane/Tile/Pf/Read/Yield".format(project=project, sample=sample, barcode=barcode))
    pf_read1_yield = xpathsum(tree, "Flowcell/Project[@name='{project}']/Sample[@name='{sample}']/Barcode[@name='{barcode}']/Lane/Tile/Pf/Read[@number='1']/Yield".format(project=project, sample=sample, barcode=barcode))
    pf_read2_yield = xpathsum(tree, "Flowcell/Project[@name='{project}']/Sample[@name='{sample}']/Barcode[@name='{barcode}']/Lane/Tile/Pf/Read[@number='2']/Yield".format(project=project, sample=sample, barcode=barcode))
    raw_yield = xpathsum(tree, "Flowcell/Project[@name='{project}']/Sample[@name='{sample}']/Barcode[@name='{barcode}']/Lane/Tile/Raw/Read/Yield".format(project=project, sample=sample, barcode=barcode))
    #pf_clusters_pc = pf_yield / raw_yield

    pf_q30 = xpathsum(tree, "Flowcell/Project[@name='{project}']/Sample[@name='{sample}']/Barcode[@name='{barcode}']/Lane/Tile/Pf/Read/YieldQ30".format(project=project, sample=sample, barcode=barcode))
    #raw_q30 = xpathsum(tree, "./Stats/Flowcell/Project[@name='{project}']/Sample[@name='{sample}']/Barcode[@name='{barcode}']/Lane/Tile/Raw/Read/YieldQ30".format(project=project, sample=sample, barcode=barcode))
    pf_read1_q30 = xpathsum(tree, "Flowcell/Project[@name='{project}']/Sample[@name='{sample}']/Barcode[@name='{barcode}']/Lane/Tile/Pf/Read[@number='1']/YieldQ30".format(project=project, sample=sample, barcode=barcode))
    pf_read2_q30 = xpathsum(tree, "Flowcell/Project[@name='{project}']/Sample[@name='{sample}']/Barcode[@name='{barcode}']/Lane/Tile/Pf/Read[@number='2']/YieldQ30".format(project=project, sample=sample, barcode=barcode))
    #pf_q30_bases_pc = pf_q30 / pf_yield

    pf_qscore_sum = xpathsum(tree, "Flowcell/Project[@name='{project}']/Sample[@name='{sample}']/Barcode[@name='{barcode}']/Lane/Tile/Pf/Read/QualityScoreSum".format(project=project, sample=sample, barcode=barcode))
    pf_qscore = pf_qscore_sum / pf_yield

    return {
        #'pf_q30_bases_pc': pf_q30_bases_pc,
        #'raw_q30': raw_q30,
        #'pf_clusters_pc': pf_clusters_pc,
        'raw_clusters': raw_clusters,
        'raw_yield': raw_yield,
        'pf_clusters': pf_clusters,
        'pf_yield': pf_yield,
        'pf_read1_yield': pf_read1_yield,
        'pf_read2_yield': pf_read2_yield,
        'pf_q30': pf_q30,
        'pf_read1_q30': pf_read1_q30,
        'pf_read2_q30': pf_read2_q30,
        'pf_qscore_sum': pf_qscore_sum,
        'pf_qscore': pf_qscore
    }


def calc_undetermined( demux_dir):
    sizes = {}
    all_files = glob.glob(demux_dir + '/l*/Project*/Sample*/*fastq.gz')
    for f in all_files:
        sample_name = re.search(r'Sample_(.*)/', f).group(1)
        if sample_name not in sizes:
            sizes[ sample_name ] = { 'size_of': 0, 'u_size_of': 0 }
        sizes[ sample_name ]['size_of'] += os.path.getsize(f)

    und_files = glob.glob(demux_dir + '/l*/Project*/Sample*/Undet*fastq.gz')
    for f in und_files:
        sample_name = re.search(r'Sample_(.*)/', f).group(1)
        sizes[ sample_name ]['u_size_of'] += os.path.getsize(f)

    proc_undetermined = {}
    for sample_name, size in sizes.items():
        proc_undetermined[ sample_name ] = float(size['u_size_of']) / size['size_of'] * 100

    return proc_undetermined

def get_raw_clusters_lane(total_sample_summary):
    """TODO: Docstring for get_raw_clusters_lane.

    Args:
        total_sample_summary (TODO): TODO

    Returns: TODO

    """
    raw_clusters_lane = dict(zip(total_sample_summary.keys(), [ 0 for t in range(len(total_sample_summary.keys())) ])) # lane: raw_clusters
    for lane, sample_summary in total_sample_summary.items():
        for sample, summary in sample_summary.items():
            raw_clusters_lane[ lane ] += summary['raw_clusters']

    return raw_clusters_lane

def parse_samples(demux_dir):
    """Takes a DEMUX dir and calculates statistics for a run on sample level.

    Args:
        demux_dir (str): the DEMUX dir

    """
    samplesheet = Samplesheet(Path(demux_dir).joinpath('SampleSheet.csv'))
    samples = list(set(samplesheet.samples()))
    lanes = list(set(samplesheet.column('lane')))

    # get all % undetermined indexes / sample
    proc_undetermined = calc_undetermined(demux_dir)

    # create a { 1: {}, 2: {}, ... } structure
    summaries = {lane_key: {} for lane_key in lanes}

    # preload the stats files
    et_stats_files = dict(zip(lanes, [ [] for t in range(len(lanes))]))
    et_index_files = dict(zip(lanes, [ [] for t in range(len(lanes))]))
    for lane in lanes:
        stats_files = glob.glob('{}/l{}t??/Stats/ConversionStats.xml'.format(demux_dir, lane))
        index_files = glob.glob('{}/l{}t??/Stats/DemultiplexingStats.xml'.format(demux_dir, lane))

        if len(stats_files) == 0:
            exit("No stats file found for sample {}".format(sample))

        if len(index_files) == 0:
            exit("No index stats file found for sample {}".format(sample))

        for f in stats_files:
            et_stats_files[lane].append(et.parse(f))

        for f in index_files:
            et_index_files[lane].append(et.parse(f))

    # get all the stats numbers
    #import ipdb; ipdb.set_trace()
    for sample in samples:
        for line in samplesheet.lines_per_column('sample_id', sample):
            lane = line['lane']
            if sample not in summaries[lane]: summaries[lane][sample] = [] # init some more

            for tree in et_stats_files[lane]:
                summaries[lane][sample].append(get_sample_summary(tree, line['project'], line['sample_name'], line['index']))

            for tree in et_index_files[ line['lane'] ]:
                summaries[lane][sample].append(get_barcode_summary(tree, line['project'], line['sample_name'], line['index']))

    # sum the numbers over a lane
    # create a { 1: {}, 2: {}, ... } structure
    total_sample_summary = dict(zip(lanes, [ {} for t in range(len(lanes))]))
    for line in samplesheet.lines():
        total_sample_summary[ line['lane'] ][ line['sample_id'] ] = {
            'raw_clusters': 0,
            'raw_yield': 0,
            'pf_clusters': 0,
            'pf_yield': 0,
            'pf_read1_yield': 0,
            'pf_read2_yield': 0,
            'pf_q30': 0,
            'pf_read1_q30': 0,
            'pf_read2_q30': 0,
            'pf_qscore_sum': 0,
            'pf_qscore': 0,
            'flowcell': line['fcid'],
            'samplename': line['sample_id'],
            'lane': line['lane'],
            'barcodes': 0,
            'perfect_barcodes': 0,
            'one_mismatch_barcodes': 0,
        }

    for lane, sample_summary in summaries.items():
        for sample, summary in sample_summary.items():
            for summary_quart in summary:
                for key, stat in summary_quart.items():
                    total_sample_summary[lane][sample][ key ] += stat

    raw_clusters_lane = get_raw_clusters_lane(total_sample_summary)

    rs= dict(zip(lanes, [ {} for t in range(len(lanes))]))
    for lane, sample_summary in total_sample_summary.items():
        for sample, summary in sample_summary.items():
            rs[ lane ][ summary['samplename'] ] = {
                'sample_name':     summary['samplename'],
                'flowcell':        summary['flowcell'],
                'lane':            lane,
                'raw_clusters_pc': round(summary['raw_clusters'] / raw_clusters_lane[lane] * 100, 2),
                'pf_clusters':     summary['pf_clusters'],
                'pf_yield_pc':     round(summary['pf_yield'] / summary['raw_yield'] * 100, 2),
                'pf_yield':        summary['pf_yield'],
                'pf_Q30':          round(summary['pf_q30'] / summary['pf_yield'] * 100, 2),
                'pf_read1_q30':    round(summary['pf_read1_q30'] / summary['pf_read1_yield'] * 100, 2),
                'pf_read2_q30':    round(summary['pf_read2_q30'] / summary['pf_read2_yield'] * 100, 2),
                'pf_qscore':       round(summary['pf_qscore_sum'] / summary['pf_yield'], 2),
                'undetermined_pc': (summary['pf_clusters'] - summary['barcodes']) / summary['pf_clusters'] * 100,
                'undetermined_proc': round(proc_undetermined[ summary['samplename'] ], 2) if summary['samplename'] in proc_undetermined else 0,
                'barcodes':         summary['barcodes'],
                'perfect_barcodes': summary['perfect_barcodes'],
                'one_mismatch_barcodes': summary['one_mismatch_barcodes'],
            }

    return rs

def parse( demux_dir):
    """Takes a DEMUX dir and calculates statistics for the run.

    Args:
        demux_dir (str): the DEMUX dir

    """

    samplesheet = Samplesheet(Path(demux_dir).joinpath('SampleSheet.csv'))
    lanes = list(set(samplesheet.column('lane')))

    # get all % undetermined indexes / sample
    proc_undetermined = calc_undetermined(demux_dir)

    # create a { 1: [], 2: [], ... } structure
    summaries = dict(zip(lanes, [ [] for t in range(len(lanes))])) # init ;)

    # preload the stats files
    et_stats_files = dict(zip(lanes, [ [] for t in range(len(lanes))]))
    et_index_files = dict(zip(lanes, [ [] for t in range(len(lanes))]))
    for lane in lanes:
        stats_files = glob.glob('{}/l{}t??/Stats/ConversionStats.xml'.format(demux_dir, lane))
        index_files = glob.glob('{}/l{}t??/Stats/DemultiplexingStats.xml'.format(demux_dir, lane))

        if len(stats_files) == 0:
            exit("No stats file found for lane {}".format(lane))

        if len(index_files) == 0:
            exit("No index stats file found for lane {}".format(lane))

        for f in stats_files:
            et_stats_files[lane].append(et.parse(f))

        for f in index_files:
            et_index_files[lane].append(et.parse(f))

    # get all the stats numbers
    for lane in lanes:

        # only parse this on lane level
        for tree in et_stats_files[lane]:
            summaries[lane].append(get_sample_summary(tree, 'all', 'all', 'all'))

        # we need barcode stats on sample level
        for line in samplesheet.lines_per_column('lane', lane):
            for tree in et_index_files[ lane ]:
                summaries[lane].append(get_barcode_summary(tree, line['project'], line['sample_name'], line['index']))

    # sum the numbers over a lane
    # create a { 1: {'raw_clusters': 0, ... } } structure
    total_lane_summary = {}
    for line in samplesheet.lines():
        total_lane_summary[ line['lane'] ] = {
            'raw_clusters': 0,
            'raw_yield': 0,
            'pf_clusters': 0,
            'pf_yield': 0,
            'pf_read1_yield': 0,
            'pf_read2_yield': 0,
            'pf_q30': 0,
            'pf_read1_q30': 0,
            'pf_read2_q30': 0,
            'pf_qscore_sum': 0,
            'pf_qscore': 0,
            'flowcell': line['fcid'],
            'samplename': line['sample_id'],
            'barcodes': 0,
            'perfect_barcodes': 0,
            'one_mismatch_barcodes': 0,
        }

    for lane, summary in summaries.items():
       for summary_quart in summary:
            for key, stat in summary_quart.items():
                total_lane_summary[lane][ key ] += stat

    rs = {} # generate a dict: raw sample name is key, value is a dict of stats
    for lane, summary in total_lane_summary.items():
        rs[ summary['samplename'] ] = {
            'sample_name':     summary['samplename'],
            'flowcell':        summary['flowcell'],
            'lane':            lane,
            'raw_clusters_pc': 100, # we still only have one sample/lane ;)
            'pf_clusters':     summary['pf_clusters'],
            'pf_yield_pc':     round(summary['pf_yield'] / summary['raw_yield'] * 100, 2),
            'pf_yield':        summary['pf_yield'],
            'pf_Q30':          round(summary['pf_q30'] / summary['pf_yield'] * 100, 2),
            'pf_read1_q30':    round(summary['pf_read1_q30'] / summary['pf_read1_yield'] * 100, 2),
            'pf_read2_q30':    round(summary['pf_read2_q30'] / summary['pf_read2_yield'] * 100, 2),
            'pf_qscore':       round(summary['pf_qscore_sum'] / summary['pf_yield'], 2),
            'undetermined_pc': (summary['pf_clusters'] - summary['barcodes']) / summary['pf_clusters'] * 100,
            'undetermined_proc': round(proc_undetermined[ summary['samplename'] ], 2) if summary['samplename'] in proc_undetermined else 0,
            'barcodes':         summary['barcodes'],
            'perfect_barcodes': summary['perfect_barcodes'],
            'one_mismatch_barcodes': summary['one_mismatch_barcodes'],
        }

    return rs

__ALL__ = [ 'parse', 'parse_samples' ]
