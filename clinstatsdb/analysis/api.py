# -*- coding: utf-8 -*-
from .models import Analysis, AnalysisSample


def samples(query=None):
    """Return a list of samples."""
    query = query or AnalysisSample.query
    query = (query.join(AnalysisSample.analysis)
                  .order_by(Analysis.analyzed_at.desc()))
    return query


def duplicates():
    """Ask the database about duplicates."""
    results = {}
    for seq_type in ('wes', 'wgs'):
        query = samples().filter(AnalysisSample.sequencing_type == seq_type)
        percentages = [sample.duplicates_percent * 100 for sample in query]
        results[seq_type] = percentages
    return results
