#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function, division

from bs4 import BeautifulSoup

def parse(demux_stats):
    """parses the Demultiplex_Stats.htm

    Args:
        demux_stats (str): a path to Demultiplex_Stats.htm of the run

    Returns: { lane: { sample_id: {}}}

    """

    def mkint(s):
        """Make sure empty strings default to 0"""
        return int('0'+s)

    def mkfloat(s):
        """Make sure empty strings default to 0"""
        return float('0'+s)

    samples = {} # lane: sample_id: {}

    soup = BeautifulSoup(open(demux_stats), 'html.parser')
    tables = soup.findAll("table")
    rows = tables[1].findAll('tr')
    for row in rows:
        sample = {}
        cols = row.findAll('td')

        lane = cols[0].string
        if not lane in samples:
            samples[lane] = {}

        sample_name = cols[1].string
        sample['sample_name'] = sample_name
        sample['barcode'] = cols[3].string
        sample['project_id'] = cols[6].string
        sample['lane'] = lane
        sample['yield_mb'] = mkint(cols[7].string.replace(",",""))
        sample['pf_pc'] = mkfloat(cols[8].string)
        sample['readcounts'] = mkint(cols[9].string.replace(",",""))
        sample['raw_clusters_pc'] = mkfloat(cols[10].string)
        sample['perfect_barcodes_pc'] = mkfloat(cols[11].string)
        sample['q30_bases_pc'] = mkfloat(cols[13].string)
        sample['mean_quality_score'] = mkfloat(cols[14].string)

        samples[lane][sample_name] = sample

    return samples
