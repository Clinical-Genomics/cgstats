# -*- coding: utf-8 -*-
from datetime import datetime
import logging

import click
import json
import yaml

from .models import Analysis
from .mip import process_all

log = logging.getLogger(__name__)


@click.group()
def analysis():
    """Interact with the post alignment part of the database."""
    pass


@analysis.command()
@click.option('-f', '--force', is_flag=True)
@click.argument('sampleinfo_file', type=click.File('r'))
@click.argument('metrics_file', type=click.File('r'))
@click.pass_context
def add(context, force, sampleinfo_file, metrics_file):
    """Load data from analysis output."""
    sampleinfo = yaml.load(sampleinfo_file)
    analysis_id = '-'.join([sampleinfo['owner'], sampleinfo['family']])
    if not force and not test_analysis(sampleinfo):
        log.warn("analysis can't be loaded, use '--force'")
        context.abort()
    else:
        old_analysis = Analysis.query.filter_by(analysis_id=analysis_id).first()
        if old_analysis:
            if force:
                log.info("removing old analysis")
                old_analysis.delete()
            else:
                log.debug("analysis already added: %s", analysis_id)
                context.abort()

    metrics = yaml.load(metrics_file)
    log.debug("parsing analysis: %s", analysis_id)
    new_analysis = process_all(analysis_id, sampleinfo, metrics)
    log.info("adding analysis: %s", new_analysis.analysis_id)
    context.obj['manager'].add_commit(new_analysis)


@analysis.command()
@click.argument('case_id')
@click.pass_context
def delete(context, case_id):
    """Delete an existing analysis and samples in the database."""
    analysis_obj = Analysis.query.filter_by(analysis_id=case_id).first()
    if analysis_obj is None:
        log.error('analysis not found in database')
        context.abort()
    analysis_obj.delete()
    context.obj['manager'].commit()
    log.info("removed analysis: %s", analysis_obj.id)


def test_analysis(sampleinfo):
    """Test if it's a supported version of MIP."""
    status = sampleinfo['analysisrunstatus']
    if status != 'finished':
        return False

    if not sampleinfo['mip_version'].startswith('v4.'):
        return False

    return True


@analysis.command()
@click.option('-c', '--condense', is_flag=True)
@click.argument('existing_data', type=click.File('r'), default='-')
@click.pass_context
def export(context, condense, existing_data):
    """Export interesting data about a case."""
    existing = yaml.load(existing_data)
    case_id = existing['case_id']
    analysis_obj = Analysis.query.filter_by(analysis_id=case_id).first()
    if analysis_obj is None:
        log.error('analysis not found in database')
        context.abort()
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

    new_data = fillin_data(existing, case_data, samples_data)

    if condense:
        raw_dump = json.dumps(new_data, default=json_serial)
    else:
        raw_dump = yaml.safe_dump(new_data, default_flow_style=False,
                                  allow_unicode=True)
    click.echo(raw_dump)


def fillin_data(existing_data, case_data, samples_data):
    """Fill in data about a case with cgstats data."""
    existing_data.update(case_data)

    # fill in sample data
    for sample_data in existing_data['samples']:
        new_data = samples_data[sample_data['id']]
        sample_data.update(new_data)

    return existing_data


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError('Type not serializable')
