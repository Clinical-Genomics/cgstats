#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function
import sys

from sqlalchemy import func
from .db import SQL
from .db.models import Datasource, Unaligned, Demux, Flowcell

def main(argv):
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
