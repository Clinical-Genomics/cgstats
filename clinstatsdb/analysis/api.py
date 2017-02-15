# -*- coding: utf-8 -*-
import datetime
from .models import Analysis, AnalysisSample

BEGINNING = datetime.datetime(1970, 1, 1)


def samples(query=None):
    """Return a list of samples."""
    query = query or AnalysisSample.query
    query = (query.join(AnalysisSample.analysis)
                  .order_by(Analysis.analyzed_at))
    return query


def duplicates():
    """Ask the database about duplicates."""
    results = {}
    for seq_type in ('wes', 'wgs'):
        query = samples().filter(AnalysisSample.sequencing_type == seq_type)
        percentages = [{
            'name': sample.sample_id,
            'y': (sample.duplicates_percent * 100)
        } for sample in query]
        results[seq_type] = percentages
    return results


def readsvscov(db):
    """Ask the database about reads vs. coverage."""
    results = {}
    for seq_type in ('wes', 'wgs'):
        query = db.query(AnalysisSample.reads_total,
                         AnalysisSample.completeness_target_20 * 100)
        query = (samples(query=query).
                 filter(AnalysisSample.sequencing_type == seq_type,
                        AnalysisSample.reads_total != None))
        results[seq_type] = [(row[0], round(row[1], 1)) for row in query]
    return results
