# -*- coding: utf-8 -*-
"""Parse QC metrics file from MIP."""
from __future__ import division
import logging

from clinstatsdb.db import Analysis, AnalysisSample

log = logging.getLogger(__name__)


def prepare(qc_metrics):
    """Take raw QC metrics and preapre for parsing."""
    family_key = qc_metrics.keys()[0]
    data = {
        'family': qc_metrics[family_key][family_key],
        'family_id': family_key,
        'samples': {key: value for key, value in qc_metrics[family_key].items()
                    if key != family_key}
    }
    return data


def parse_family(qc_family):
    """Parse our version from family section of data."""
    versions = {
        'samtools': qc_family['Program']['Samtools']['Version'],
        'gatk': str(qc_family['Program']['GATK']['Version']),
        'freebayes': qc_family['Program']['Freebayes']['Version'],
    }
    return versions


def parse_sample(qc_sample):
    """Parse out relevant information from sample data."""
    data = {}
    for key, value in qc_sample.items():
        if 'lanes' in key:
            # alignment
            hs_metrics = value['CalculateHsMetrics']['Header']['Data']
            mult_metrics = value['CollectMultipleMetrics']['Header']['Pair']
            data['strand_balance'] = mult_metrics['STRAND_BALANCE']
            data['sex_predicted'] = value['ChanjoSexCheck']['gender']

            # coverage
            data['coverage_target'] = hs_metrics['MEAN_TARGET_COVERAGE']
            data['completeness_target_10'] = hs_metrics['PCT_TARGET_BASES_10X']
            data['completeness_target_20'] = hs_metrics['PCT_TARGET_BASES_20X']
            data['completeness_target_50'] = hs_metrics['PCT_TARGET_BASES_50X']
            data['completeness_target_100'] = hs_metrics['PCT_TARGET_BASES_100X']

            # variants
            comp_overlap = (value['VariantEval_All']['CompOverlap_header']
                                 ['CompOverlap_data_all'])
            variant_sum = (value['VariantEval_All']['VariantSummary_header']
                                ['VariantSummary_data_all'])
            variant_count = (value['VariantEval_All']['CountVariants_header']
                                  ['CountVariants_data_all'])
            data['variants'] = comp_overlap['nEvalVariants']
            data['indels'] = variant_sum['nIndels']
            data['snps'] = variant_sum['nSNPs']
            data['titv_ratio'] = variant_sum['TiTvRatio']
            data['novel_sites'] = comp_overlap['novelSites']
            data['concordant_rate'] = comp_overlap['concordantRate'] / 100
            data['hethom_ratio'] = variant_count['hetHomRatio']

    data['reads_total'] = qc_sample['TotalReads']
    data['mapped_percent'] = qc_sample['MappedRate']
    data['duplicates_percent'] = qc_sample['Duplicates']
    return data


def process_samples(qc_samples, sequencing_type):
    """Build models from QC metrics output."""
    for sample_id, sample_values in qc_samples.items():
        log.info("adding sample: %s", sample_id)
        sample_data = parse_sample(sample_values)
        sample_obj = AnalysisSample(sample_id=sample_id,
                                    sequencing_type=sequencing_type,
                                    **sample_data)
        yield sample_obj


def process_analysis(qc_sampleInfo):
    """Build analysis model from QC sample info file."""
    data = {'pipeline': 'mip'}
    family_key = qc_sampleInfo.keys()[0]
    data['analysis_id'] = get_analysisid(qc_sampleInfo)
    data['pipeline_version'] = qc_sampleInfo[family_key][family_key]['MIPVersion']
    data['analyzed_at'] = qc_sampleInfo[family_key][family_key]['AnalysisDate']

    rank_model = (qc_sampleInfo[family_key][family_key]['Program']
                               ['RankVariants']['RankModel']['Version'])
    data['program_versions'] = dict(rank_model=rank_model)
    analysis_type = qc_sampleInfo[family_key][family_key]['AnalysisType']
    # this should really be found from LIMS... and be on sample level!
    sequencing_type = dict(exomes='wes', genomes='wgs').get(analysis_type)
    return Analysis(**data), sequencing_type


def get_capturekits(pedigree):
    """Parse out capture kits used for samples."""
    family_key = pedigree.keys()[0]
    samples = {sample_id: data.get('Capture_kit', [None])[0] for
               sample_id, data in pedigree[family_key].items()}
    return samples


def process_all(pedigree, qc_sampleInfo, qc_metrics):
    """Process all data."""
    new_analysis, sequencing_type = process_analysis(qc_sampleInfo)
    data = prepare(qc_metrics)
    program_versions = parse_family(data['family'])
    program_versions['rank_model'] = new_analysis.program_versions['rank_model']
    new_analysis.program_versions = program_versions
    new_samples = list(process_samples(data['samples'], sequencing_type))
    ped_samples = get_capturekits(pedigree)
    for new_sample in new_samples:
        new_sample.capture_kit = ped_samples[new_sample.sample_id]

    new_analysis.samples = new_samples
    return new_analysis


def get_analysisid(sample_info):
    family_key = sample_info.keys()[0]
    customer = sample_info[family_key][family_key]['InstanceTag'][0]
    identifier = "{}-{}".format(customer, family_key)
    return identifier
