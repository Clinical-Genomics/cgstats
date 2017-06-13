#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function
import sys
from pprint import pprint
from .utils import xstats
import pstats
import cProfile


def main(argv):
    
    #print(Supportparams.exists('/home/clinical/DEMUX//150703_D00134_0206_AH5HGFBCXX/Unaligned4/support.txt')) # 515
    #print(Datasource.exists('/home/clinical/DEMUX//150703_D00134_0206_AH5HGFBCXX/Unaligned4/Basecall_Stats_H5HGFBCXX/Demultiplex_Stats.htm')) #515
    #print(Flowcell.exists('H5HGFBCXX')) # 512
    #print(Demux.exists(512, 'Y101,I8,I8,Y101')) # 474
    #print(Project.exists('240540')) #552
    #print(Sample.exists('ADM1136A1_XTA08', 'CAGCGTTA')) #6651
    #print(Unaligned.exists(18, 487, 1)) #13902

    #pprint(xstats.parse_samples('/mnt/hds/proj/bioinfo/DEMUX/160308_ST-E00269_0055_AHK5VKCCXX/'))
    pprint(xstats.parse_samples('/mnt/hds/proj/bioinfo/DEMUX/161125_ST-E00269_0150_AH37GVALXX'))
    pprint(xstats.parse_samples('/mnt/hds/proj/bioinfo/DEMUX/161125_ST-E00269_0150_AH37GVALXX'))
    #pprint(xstats.parse_samples('/mnt/hds/proj/bioinfo/DEMUX/160308_ST-E00269_0055_AHK5VKCCXX/'))

    #print(Backup.exists('151117_D00410_0187_AHWYGMADXX'))
    #print(Backup.exists('141212_D00134_0166_AHB058ADXX'))
    #print(Backup.exists('131219_D00134_0057_BH829YADXX'))
    #print(Backup.exists('141028_D00410_0109_AHAH5WADXX'))
    #print(Backup.exists('131219_D00134_0057_BH829YADXX', 'tape005_006'))
    #print(Backup.exists('131219_D00134_0057_BH829YADXX', 'tape007_005'))

if __name__ == '__main__':
    outfile = 'xpathstats_bs_fqp_parse'
    cProfile.run('xstats.parse("/mnt/hds/proj/bioinfo/DEMUX/161125_ST-E00269_0150_AH37GVALXX")', outfile)
    p = pstats.Stats(outfile)
    p.sort_stats('cumtime').print_stats(10)

    outfile = 'xpathstats_bs_fqp_samples_parse'
    cProfile.run('xstats.parse_samples("/mnt/hds/proj/bioinfo/DEMUX/161125_ST-E00269_0150_AH37GVALXX")', outfile)
    p = pstats.Stats(outfile)
    p.sort_stats('cumtime').print_stats(10)
