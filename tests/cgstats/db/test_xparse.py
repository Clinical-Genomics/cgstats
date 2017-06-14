#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import pytest
from path import Path

from cgstats.db.xparse import gather_supportparams, gather_datasource, gather_demux

def test_gather_supportparams(x_run_dir, x_pooled_missing_logs_run_dir, x_pooled_missing_unaligned_run_dir):

    with pytest.raises(IOError):
        gather_supportparams(x_pooled_missing_logs_run_dir)

    with pytest.raises(IOError):
        gather_supportparams(x_pooled_missing_unaligned_run_dir)

    assert gather_supportparams(x_run_dir) == {
            'idstring': 'bcl2fastq v2.15.0.4',
            'commandline': '/usr/local/bin/bcl2fastq -d 2 -r 4 -w 4 -p 14 --tiles s_1_11 --tiles s_1_12 -R /scratch/743545//mnt/hds2/proj/bioinfo/Runs/170202_ST-E00269_0169_AHC7H2ALXX -o /scratch/743545/Xout --barcode-mismatches 1 --use-bases-mask Y151,I8,Y151',
            'time': '20170205061756',
            'program': '/usr/local/bin/bcl2fastq',
            'sampleconfig_path': str(Path(x_run_dir).joinpath('SampleSheet.csv')),
            'sampleconfig': '[Data]\n'
'FCID,Lane,SampleID,SampleRef,index,SampleName,Control,Recipe,Operator,Project\n'
'HC7H2ALXX,1,SVE2274A2_TCCGCGAA,hg19,TCCGCGAA,659262,N,R1,NN,659262\n'
'HC7H2ALXX,2,SVE2274A4_TCCGCGAA,hg19,TCCGCGAA,659262,N,R1,NN,659262\n'
'HC7H2ALXX,3,SVE2274A6_TCCGCGAA,hg19,TCCGCGAA,659262,N,R1,NN,659262\n'
'HC7H2ALXX,4,SVE2274A7_TCCGCGAA,hg19,TCCGCGAA,659262,N,R1,NN,659262\n'
'HC7H2ALXX,5,SVE2274A8_TCCGCGAA,hg19,TCCGCGAA,659262,N,R1,NN,659262\n'
'HC7H2ALXX,6,SVE2274A9_TCTCGCGC,hg19,TCTCGCGC,659262,N,R1,NN,659262\n'
'HC7H2ALXX,7,SVE2274A10_TCTCGCGC,hg19,TCTCGCGC,659262,N,R1,NN,659262\n'
'HC7H2ALXX,8,SVE2274A11_TCTCGCGC,hg19,TCTCGCGC,659262,N,R1,NN,659262',
            'document_path': str(Path(x_run_dir).joinpath('Unaligned'))
    }

def test_gather_datasource(x_run_dir, x_pooled_missing_logs_run_dir):

    with pytest.raises(IOError):
        gather_datasource(x_pooled_missing_logs_run_dir)

    assert gather_datasource(x_run_dir) == {
            'runname': str(Path(x_run_dir).normpath().basename()),
            'rundate': '170202',
            'machine': 'ST-E00269',
            'servername': socket.gethostname(),
            'document_path': str(Path(x_run_dir).joinpath('l1t11/Stats/ConversionStats.xml'))
    }

def test_gather_demux(x_run_dir, x_pooled_missing_logs_run_dir):

    with pytest.raises(IOError):
        gather_demux(x_pooled_missing_logs_run_dir)

    assert gather_demux(x_run_dir) == {
        'basemask': 'Y151,I8,Y151'
    }
