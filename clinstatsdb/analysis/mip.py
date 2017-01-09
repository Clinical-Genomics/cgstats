# -*- coding: utf-8 -*-
"""Parse QC metrics file from MIP."""
from __future__ import division
import logging

from .models import Analysis, AnalysisSample

log = logging.getLogger(__name__)


def parse_versions(qcmetrics):
    """Parse our version from family section of data."""
    versions = {}
    programs = ['samtools', 'gatk', 'freebayes', 'genmod', 'manta']
    for program in programs:
        program_data = qcmetrics['program'].get(program)
        if program_data:
            versions[program] = str(program_data['version'])
        else:
            log.warn("missing version info for: %s", program)
    return versions


def build_sample(sample_id, sample_data, seq_type):
    """Parse out relevant information from sample data."""
    data = dict(sample_id=sample_id, sequencing_type=seq_type)
    for key, value in sample_data.items():
        if '_lanes_' in key:
            # alignment
            hs_metrics = value['calculatehsmetrics']['header']['data']
            mult_metrics = value['collectmultiplemetrics']['header']['pair']
            data['strand_balance'] = mult_metrics['STRAND_BALANCE']
            data['sex_predicted'] = value['chanjo_sexcheck']['gender']

            # coverage
            data['coverage_target'] = hs_metrics['MEAN_TARGET_COVERAGE']
            data['completeness_target_10'] = hs_metrics['PCT_TARGET_BASES_10X']
            data['completeness_target_20'] = hs_metrics['PCT_TARGET_BASES_20X']
            data['completeness_target_50'] = hs_metrics['PCT_TARGET_BASES_50X']
            data['completeness_target_100'] = hs_metrics['PCT_TARGET_BASES_100X']

            # variants
            comp_overlap = (value['variantevalall']['comp_overlap_header']
                                 ['comp_overlap_data_all'])
            variant_sum = (value['variantevalall']['variant_summary_header']
                                ['variant_summary_data_all'])
            variant_count = (value['variantevalall']['count_variants_header']
                                  ['count_variants_data_all'])
            data['variants'] = comp_overlap['nEvalVariants']
            data['indels'] = variant_sum['nIndels']
            data['snps'] = variant_sum['nSNPs']
            data['titv_ratio'] = variant_sum['TiTvRatio']
            data['novel_sites'] = comp_overlap['novelSites']
            data['concordant_rate'] = comp_overlap['concordantRate'] / 100
            data['hethom_ratio'] = variant_count['hetHomRatio']

            data['duplicates_percent'] = (value['markduplicates']
                                               ['fraction_duplicates'])

    data['reads_total'] = sample_data['reads']
    data['mapped_percent'] = sample_data['reads_mapped_rate']

    new_sample = AnalysisSample(**data)
    return new_sample


def build_analysis(analysis_id, sampleinfo):
    """Build analysis model from QC sample info file."""
    rank_model = sampleinfo['program']['rankvariant']['rank_model']['version']
    data = dict(
        pipeline='mip',
        analysis_id=analysis_id,
        pipeline_version=sampleinfo['mip_version'],
        analyzed_at=sampleinfo['analysis_date'],
        program_versions=dict(rank_model=rank_model),
    )
    return Analysis(**data)


def process_all(analysis_id, sampleinfo, qcmetrics):
    """Process all data."""
    new_analysis = build_analysis(analysis_id, sampleinfo)
    # parse out program versions
    versions = parse_versions(qcmetrics)
    versions['rank_model'] = new_analysis.program_versions['rank_model']
    new_analysis.program_versions = versions

    for sample_id, sample_data in qcmetrics['sample'].items():
        log.info("adding sample: %s", sample_id)
        seq_type = sampleinfo['analysis_type'][sample_id]
        new_sample = build_sample(sample_id, sample_data, seq_type)
        capture_kit = sampleinfo['sample'][sample_id].get('capture_kit')
        new_sample.capture_kit = capture_kit
        new_analysis.samples.append(new_sample)

    return new_analysis
