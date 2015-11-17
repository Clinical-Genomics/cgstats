#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function
import sys

from sqlalchemy import func
from .db import SQL
from .db.models import Datasource, Unaligned, Demux, Flowcell, Supportparams, Project, Sample, Backup
from .utils import xstats

def main(argv):

    print(Supportparams.exists('/home/clinical/DEMUX//150703_D00134_0206_AH5HGFBCXX/Unaligned4/support.txt')) # 515
    print(Datasource.exists('/home/clinical/DEMUX//150703_D00134_0206_AH5HGFBCXX/Unaligned4/Basecall_Stats_H5HGFBCXX/Demultiplex_Stats.htm')) #515
    print(Flowcell.exists('H5HGFBCXX')) # 512
    print(Demux.exists(512, 'Y101,I8,I8,Y101')) # 474
    print(Project.exists('240540')) #552
    print(Sample.exists('ADM1136A1_XTA08', 'CAGCGTTA')) #6651
    print(Unaligned.exists(18, 487, 1)) #13902

    print(xstats.parse('/mnt/hds/proj/bioinfo/DEMUX/151009_ST-E00198_0059_BH2V2YCCXX'))

    print(Backup.exists('151117_D00410_0187_AHWYGMADXX'))
    print(Backup.exists('141212_D00134_0166_AHB058ADXX'))
    print(Backup.exists('131219_D00134_0057_BH829YADXX'))
    print(Backup.exists('131219_D00134_0057_BH829YADXX', 'tape005_006'))
    print(Backup.exists('131219_D00134_0057_BH829YADXX', 'tape007_005'))

    rs = SQL.query(
        func.year(Datasource.rundate).label('year'),\
        func.month(Datasource.rundate).label('month'),\
        func.count(Datasource.datasource_id.distinct()).label('runs'),\
        func.round(func.sum(Unaligned.readcounts / 2000000), 2).label('mil reads'),\
        func.round(func.sum(Unaligned.readcounts) / (func.count(Datasource.datasource_id.distinct())*2000000), 1).label('mil reads fc lane')
    ).\
    outerjoin(Demux).\
    outerjoin(Flowcell).\
    outerjoin(Unaligned).\
    group_by(func.year(Datasource.rundate), func.month(Datasource.rundate)).\
    order_by(func.year(Datasource.rundate).desc(), func.month(Datasource.rundate).desc(), func.day(Datasource.rundate).desc()).\
    all()

    print(rs)

if __name__ == '__main__':
    main(sys.argv[1:])
