# -*- coding: utf-8 -*-
import logging

from .models import Analysis

log = logging.getLogger(__name__)


def fillin_data(existing_data, case_data, samples_data):
    """Fill in data about a case with cgstats data."""
    existing_data.update(case_data)

    # filter out samples that are not in the analysis
    relevant_samples = []
    for sample_data in existing_data['samples']:
        if sample_data['id'] in samples_data:
            relevant_samples.append(sample_data)
        else:
            log.warn("skipping sample: %s", sample_data['id'])
    existing_data['samples'] = relevant_samples

    # fill in sample data
    for sample_data in existing_data['samples']:
        new_data = samples_data[sample_data['id']]
        sample_data.update(new_data)

    return existing_data


def export_run(cgstats_db, existing_data):
    """Fill in export information based on LIMS data."""
    case_id = existing_data['case_id']
    analysis_obj = Analysis.query.filter_by(analysis_id=case_id).first()
    if analysis_obj is None:
        log.error('analysis not found in database')
        return None
    case_data = {
        'pipeline': analysis_obj.pipeline,
        'pipeline_version': analysis_obj.pipeline_version,
        'analysis_date': analysis_obj.analyzed_at,
    }
    samples_data = {}
    for sample_obj in analysis_obj.samples:
        sample_data = {
            'sequencing_type': sample_obj.sequencing_type,
            'sex_predicted': sample_obj.sex_predicted,
            'read_pairs': sample_obj.read_pairs,
            'mapped': sample_obj.mapped_percent,
            'duplicates': sample_obj.duplicates_percent,
            'target_coverage': sample_obj.coverage_target,
            'target_completeness': sample_obj.completeness_target_10,
        }
        samples_data[sample_obj.sample_id] = sample_data

    new_data = fillin_data(existing_data, case_data, samples_data)
    return new_data
