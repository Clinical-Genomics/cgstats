#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function, division

import xml.etree.cElementTree as et
import glob
import re
import os
import logging

from path import Path

from demux.utils import iseqSampleSheet


log = logging.getLogger(__name__)


def xpathsum(tree, xpath):
    """Sums all numbers found at these xpath nodes

    Args:
        tree (an elementTree): parsed XML as an elementTree
        xpath (str): an xpath the XML nodes

    Returns (int): the sum of all nodes

    """
    numbers = tree.findall(xpath)
    return sum((int(number.text) for number in numbers))


def get_barcode_summary(tree, project, sample, barcode, lane):
    """Calculates following statistics from the DemultiplexingStats file
    * BarcodeCount
    * PerfectBarcodeCount
    * OneMismatchBarcodeCount

    Args:
        tree (an elementTree: parsed XML as an elementTree

    Returns: TODO

    """

    barcodes = xpathsum(tree, f"Flowcell/Project[@name='{project}']/Sample/"
                              f"Barcode[@name='{barcode}']/Lane[@number='{lane}']/BarcodeCount")

    perfect_barcodes = xpathsum(tree, f"Flowcell/Project[@name='{project}']/Sample/"
                                      f"Barcode[@name='{barcode}']/Lane[@number='{lane}']/"
                                      f"PerfectBarcodeCount")

    one_mismatch_barcodes = xpathsum(tree, f"Flowcell/Project[@name='{project}']/Sample/"
                                           f"Barcode[@name='{barcode}']/Lane[@number='{lane}']/"
                                           f"OneMismatchBarcodeCount")

    return {
        'barcodes': barcodes,
        'perfect_barcodes': perfect_barcodes,
        'one_mismatch_barcodes': one_mismatch_barcodes,
    }


def get_sample_summary(tree, project, sample, barcode, lane):
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
        lane(str): A lane number

    Returns (dict): with following keys: pf_clusters, pf_yield, pf_q30, pf_read1_yield, pf_read2_yield,
                    pf_read1_q30, pf_read2_q30, pf_qscore_sum, pf_qscore

    """
    raw_clusters = xpathsum(tree, f"Flowcell/Project[@name='{project}']/Sample/"
                                  f"Barcode[@name='{barcode}']/Lane[@number='{lane}']/Tile/Raw/"
                                  f"ClusterCount")
    pf_clusters = xpathsum(tree, f"Flowcell/Project[@name='{project}']/Sample/"
                                 f"Barcode[@name='{barcode}']/Lane[@number='{lane}']/Tile/Pf/"
                                 f"ClusterCount")
    pf_yield = xpathsum(tree, f"Flowcell/Project[@name='{project}']/Sample/"
                              f"Barcode[@name='{barcode}']/Lane[@number='{lane}']/Tile/Pf/Read/Yield")

    log.debug("\tpf_yield={}".format(pf_yield))

    pf_read1_yield = xpathsum(tree, f"Flowcell/Project[@name='{project}']/Sample/"
                                    f"Barcode[@name='{barcode}']/Lane[@number='{lane}']/Tile/Pf/"
                                    f"Read[@number='1']/Yield")

    pf_read2_yield = xpathsum(tree, f"Flowcell/Project[@name='{project}']/Sample/"
                                    f"Barcode[@name='{barcode}']/Lane[@number='{lane}']/Tile/Pf/"
                                    f"Read[@number='2']/Yield")

    raw_yield = xpathsum(tree, f"Flowcell/Project[@name='{project}']/Sample/"
                               f"Barcode[@name='{barcode}']/Lane[@number='{lane}']/Tile/Raw/Read/"
                               f"Yield")

    pf_q30 = xpathsum(tree, f"Flowcell/Project[@name='{project}']/Sample/"
                            f"Barcode[@name='{barcode}']/Lane[@number='{lane}']/Tile/Pf/Read/YieldQ30")

    pf_read1_q30 = xpathsum(tree, f"Flowcell/Project[@name='{project}']/Sample/"
                                  f"Barcode[@name='{barcode}']/Lane[@number='{lane}']/Tile/Pf/"
                                  f"Read[@number='1']/YieldQ30")

    pf_read2_q30 = xpathsum(tree, f"Flowcell/Project[@name='{project}']/Sample/"
                                  f"Barcode[@name='{barcode}']/Lane[@number='{lane}']/Tile/Pf/"
                                  f"Read[@number='2']/YieldQ30")

    pf_qscore_sum = xpathsum(tree, f"Flowcell/Project[@name='{project}']/Sample/"
                                   f"Barcode[@name='{barcode}']/Lane[@number='{lane}']/Tile/Pf/"
                                   f"Read/QualityScoreSum")

    pf_qscore = pf_qscore_sum / pf_yield if pf_yield != 0 else 0

    return {
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


def calc_undetermined(demux_dir):
    sizes = {}
    all_files = glob.glob(demux_dir + '/l*/Project*/Sample*/*fastq.gz')
    for f in all_files:
        sample_name = re.search(r'Sample_(.*)/', f).group(1)
        if sample_name not in sizes:
            sizes[sample_name] = {'size_of': 0, 'u_size_of': 0}
        sizes[sample_name]['size_of'] += os.path.getsize(f)

    und_files = glob.glob(demux_dir + '/l*/Project*/Sample*/Undet*fastq.gz')
    for f in und_files:
        sample_name = re.search(r'Sample_(.*)/', f).group(1)
        sizes[sample_name]['u_size_of'] += os.path.getsize(f)

    proc_undetermined = {}
    for sample_name, size in sizes.items():
        proc_undetermined[sample_name] = float(size['u_size_of']) / size['size_of'] * 100

    return proc_undetermined


def get_raw_clusters_lane(total_sample_summary):
    """TODO: Docstring for get_raw_clusters_lane.

    Args:
        total_sample_summary (TODO): TODO

    Returns: TODO

    """
    raw_clusters_lane = dict(zip(total_sample_summary.keys(), [0 for t in range(len(total_sample_summary.keys()))]))  # lane: raw_clusters
    for lane, sample_summary in total_sample_summary.items():
        for sample, summary in sample_summary.items():
            raw_clusters_lane[lane] += summary['raw_clusters']

    return raw_clusters_lane


def parse_samples(unaligned_dir):
    """Takes a DEMUX dir and calculates statistics for a run on sample level.

    Args:
        demux_dir (str): the DEMUX dir

    """
    log.debug("Parsing sample stats ...")

    samplesheet = iseqSampleSheet(Path(unaligned_dir).joinpath('SampleSheet.csv'))
    samples = list(set(samplesheet.samples()))
    lanes = [1]

    # create a { 1: {}, 2: {}, ... } structure
    summaries = {lane_key: {} for lane_key in lanes}

    stats_file = f"{unaligned_dir}/Stats/ConversionStats.xml"
    index_file = f"{unaligned_dir}/Stats/DemultiplexingStats.xml"

    et_stats_file = et.parse(stats_file)

    et_index_file = et.parse(index_file)

    # get all the stats numbers
    for sample in samples:
        log.debug("Getting stats for '{}'...".format(sample))
        for line in samplesheet.lines_per_column('sample_id', sample):

            # in case of dualindex, convert to iseq format (separated by '+' instead of '-')
            barcode = line.dualindex.replace('-', '+')
            lane = 1
            log.debug("...for lane {}".format(lane))
            if sample not in summaries[lane]:
                summaries[lane][sample] = []  # init some more

            summaries[lane][sample].append(get_sample_summary(et_stats_file, line['project'],
                                                              line['sample_name'],
                                                              barcode, lane))

            summaries[lane][sample].append(get_barcode_summary(et_index_file, line['project'],
                                                               line['sample_name'],
                                                               barcode, lane))

    # sum the numbers over a lane
    # create a { 1: {}, 2: {}, ... } structure
    total_sample_summary = dict(zip(lanes, [{} for t in range(len(lanes))]))
    for line in samplesheet.lines():
        total_sample_summary[1][line['sample_id']] = {
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
            'lane': 1,
            'barcodes': 0,
            'perfect_barcodes': 0,
            'one_mismatch_barcodes': 0,
        }

    for lane, sample_summary in summaries.items():
        for sample, summary in sample_summary.items():
            for summary_quart in summary:
                for key, stat in summary_quart.items():
                    total_sample_summary[lane][sample][key] += stat

    raw_clusters_lane = get_raw_clusters_lane(total_sample_summary)

    rs = dict(zip(lanes, [{} for t in range(len(lanes))]))
    for lane, sample_summary in total_sample_summary.items():
        for sample, summary in sample_summary.items():
            rs[lane][summary['samplename']] = {
                'sample_name':     summary['samplename'],
                'flowcell':        summary['flowcell'],
                'lane':            lane,
                'raw_clusters_pc': round(summary['raw_clusters'] / raw_clusters_lane[lane] * 100, 2) if raw_clusters_lane[lane] else 0,
                'pf_clusters':     summary['pf_clusters'],
                'pf_yield_pc':     round(summary['pf_yield'] / summary['raw_yield'] * 100, 2) if summary['raw_yield'] else 0,
                'pf_yield':        summary['pf_yield'],
                'pf_Q30':          round(summary['pf_q30'] / summary['pf_yield'] * 100, 2) if summary['pf_yield'] else 0,
                'pf_read1_q30':    round(summary['pf_read1_q30'] / summary['pf_read1_yield'] * 100, 2) if summary['pf_read1_yield'] else 0,
                'pf_read2_q30':    round(summary['pf_read2_q30'] / summary['pf_read2_yield'] * 100, 2) if summary['pf_read2_yield'] else 0,
                'pf_qscore':       round(summary['pf_qscore_sum'] / summary['pf_yield'], 2) if summary['pf_yield'] else 0,
                'undetermined_pc': (summary['pf_clusters'] - summary['barcodes']) / summary['pf_clusters'] * 100 if summary['pf_clusters'] else 0,
                'barcodes':         summary['barcodes'],
                'perfect_barcodes': summary['perfect_barcodes'],
                'one_mismatch_barcodes': summary['one_mismatch_barcodes'],
            }

    return rs


def parse(unaligned_dir):
    """Takes a DEMUX dir and calculates statistics for the run.

    Args:
        demux_dir (str): the DEMUX dir

    """
    log.debug("Parsing on lane level ...")

    samplesheet = iseqSampleSheet(Path(unaligned_dir).joinpath('SampleSheet.csv'))
    lanes = [1]

    # create a { 1: [], 2: [], ... } structure
    summaries = dict(zip(lanes, [[] for t in range(len(lanes))]))  # init ;)

    stats_file = f"{unaligned_dir}Stats/ConversionStats.xml"
    index_file = f"{unaligned_dir}Stats/DemultiplexingStats.xml"

    # preload the stats files
    et_stats_file = et.parse(stats_file)
    et_index_file = et.parse(index_file)

    # get all the stats numbers
    for lane in lanes:

        # only parse this on lane level
        summaries[lane].append(get_sample_summary(et_stats_file, 'all', 'all', 'all', lane))

        # we need barcode stats on sample level
        for line in samplesheet.lines_per_column('lane', lane):
            summaries[lane].append(get_barcode_summary(et_index_file, line['project'],
                                                       line['sample_name'], line.dualindex, lane))

    # sum the numbers over a lane
    # create a { 1: {'raw_clusters': 0, ... } } structure
    total_lane_summary = {}
    for line in samplesheet.lines():
        total_lane_summary[line['lane']] = {
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
                total_lane_summary[lane][key] += stat

    rs = {}  # generate a dict: raw sample name is key, value is a dict of stats
    for lane, summary in total_lane_summary.items():
        rs[lane] = {
            'sample_name':     summary['samplename'],
            'flowcell':        summary['flowcell'],
            'lane':            lane,
            'raw_clusters_pc': 100,  # we still only have one sample/lane ;)
            'pf_clusters':     summary['pf_clusters'],
            'pf_yield_pc':     round(summary['pf_yield'] / summary['raw_yield'] * 100, 2) if summary['raw_yield'] else 0,
            'pf_yield':        summary['pf_yield'],
            'pf_Q30':          round(summary['pf_q30'] / summary['pf_yield'] * 100, 2) if summary['pf_yield'] else 0,
            'pf_read1_q30':    round(summary['pf_read1_q30'] / summary['pf_read1_yield'] * 100, 2) if summary['pf_read1_yield'] else 0,
            'pf_read2_q30':    round(summary['pf_read2_q30'] / summary['pf_read2_yield'] * 100, 2) if summary['pf_read2_yield'] else 0,
            'pf_qscore':       round(summary['pf_qscore_sum'] / summary['pf_yield'], 2) if summary['pf_yield'] else 0,
            'undetermined_pc': (summary['pf_clusters'] - summary['barcodes']) / summary['pf_clusters'] * 100 if summary['pf_clusters'] else 0,
            'barcodes':         summary['barcodes'],
            'perfect_barcodes': summary['perfect_barcodes'],
            'one_mismatch_barcodes': summary['one_mismatch_barcodes'],
        }

    return rs


__ALL__ = ['parse', 'parse_samples']
