#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
from datetime import datetime
from path import Path

from cgstats.db.parse import gather_supportparams, gather_datasource

def test_gather_supportparams(rapid_run_dir):
    demuxdir = Path(rapid_run_dir)
    assert gather_supportparams(demuxdir, 'Unaligned') == {
        'idstring': 'bcl2fastq-1.8.4',
        'program': '/usr/local/bin/configureBclToFastq.pl',
        'command': {
            '--output-dir': 'DEMUX/150114_D00134_0168_AHB07NADXX/Unaligned',
            '--fastq-cluster-count': '0',
            '--sample-sheet': 'tests/fixtures/150114_D00134_0168_AHB07NADXX/Data/Intensities/BaseCalls/SampleSheet.csv',
            '--input-dir': 'tests/fixtures/150114_D00134_0168_AHB07NADXX/Data/Intensities/BaseCalls',
            '--use-bases-mask': 'Y101,I6n,Y101'
        },
        'system': {
            'OS': 'linux',
            'PID': '47668',
            'PERL_VERSION': 'v5.10.1',
            'PERL_EXECUTABLE': '/usr/bin/perl'
        },
        'document_path': str(demuxdir.joinpath('Unaligned', 'support.txt')),
        'commandline': '/usr/local/bin/configureBclToFastq.pl --sample-sheet tests/fixtures/150114_D00134_0168_AHB07NADXX/Data/Intensities/BaseCalls/SampleSheet.csv --use-bases-mask Y101,I6n,Y101 --fastq-cluster-count 0 --input-dir tests/fixtures/150114_D00134_0168_AHB07NADXX/Data/Intensities/BaseCalls --output-dir DEMUX/150114_D00134_0168_AHB07NADXX/Unaligned',
        'sampleconfig_path': str(demuxdir.joinpath('SampleSheet.csv')),
        'sampleconfig': 'FCID,Lane,SampleID,SampleRef,Index,Description,Control,Recipe,Operator,SampleProject\r\n'
                        'HB07NADXX,1,SIB911A1_sureselect4,hg19,TGACCA,959191,N,R1,NN,959191\r\n'
                        'HB07NADXX,1,SIB911A2_sureselect5,hg19,ACAGTG,959191,N,R1,NN,959191\r\n'
                        'HB07NADXX,1,SIB910A3_sureselect6,hg19,GCCAAT,454557,N,R1,NN,454557\r\n'
                        'HB07NADXX,1,SIB914A2_sureselect2,hg19,CGATGT,504910,N,R1,NN,504910\r\n'
                        'HB07NADXX,1,SIB914A11_sureselect11,hg19,GGCTAC,504910,N,R1,NN,504910\r\n'
                        'HB07NADXX,1,SIB914A12_sureselect12,hg19,CTTGTA,504910,N,R1,NN,504910\r\n'
                        'HB07NADXX,1,SIB914A15_sureselect15,hg19,GAAACC,504910,N,R1,NN,504910\r\n'
                        'HB07NADXX,2,SIB911A1_sureselect4,hg19,TGACCA,959191,N,R1,NN,959191\r\n'
                        'HB07NADXX,2,SIB911A2_sureselect5,hg19,ACAGTG,959191,N,R1,NN,959191\r\n'
                        'HB07NADXX,2,SIB910A3_sureselect6,hg19,GCCAAT,454557,N,R1,NN,454557\r\n'
                        'HB07NADXX,2,SIB914A2_sureselect2,hg19,CGATGT,504910,N,R1,NN,504910\r\n'
                        'HB07NADXX,2,SIB914A11_sureselect11,hg19,GGCTAC,504910,N,R1,NN,504910\r\n'
                        'HB07NADXX,2,SIB914A12_sureselect12,hg19,CTTGTA,504910,N,R1,NN,504910\r\n'
                        'HB07NADXX,2,SIB914A15_sureselect15,hg19,GAAACC,504910,N,R1,NN,504910\r\n',
        'time': datetime(2017, 3, 10, 16, 14, 55, 233857)
        }


def test_gather_datasource(rapid_run_dir):
    assert gather_datasource(Path(rapid_run_dir)) == {
        'rundate': u'150114',
        'machine': u'D00134',
        'runname': '150114_D00134_0168_AHB07NADXX',
        'servername': socket.gethostname()
    }

#'basemask': 'Y101,I6n,Y101',
#        'flowcell_pos': u'A',
#        'flowcell': 'HB07NADXX',
