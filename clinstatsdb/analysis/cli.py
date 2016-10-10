# -*- coding: utf-8 -*-
import logging

import click
import yaml

from .models import Analysis
from .mip import process_all, get_analysisid

log = logging.getLogger(__name__)


@click.group()
def analysis():
    """Interact with the post alignment part of the database."""
    pass


@analysis.command()
@click.option('-f', '--force', is_flag=True)
@click.argument('sampleinfo_file', type=click.File('r'))
@click.argument('metrics_file', type=click.File('r'))
@click.argument('qcpedigree_file', type=click.File('r'))
@click.pass_context
def add(context, force, sampleinfo_file, metrics_file, qcpedigree_file):
    """Load data from analysis output."""
    sample_info = yaml.load(sampleinfo_file)
    analysis_id = get_analysisid(sample_info)
    if not force and not test_analysis(sample_info):
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

    pedigree = yaml.load(qcpedigree_file)
    metrics = yaml.load(metrics_file)
    log.debug("parsing analysis: %s", analysis_id)
    new_analysis = process_all(pedigree, sample_info, metrics)
    log.info("adding analysis: %s", new_analysis.id)
    context.obj['manager'].add_commit(new_analysis)


def test_analysis(sample_info):
    """Test if it's a supported version of MIP."""
    family_key = sample_info.keys()[0]
    status = sample_info[family_key][family_key]['AnalysisRunStatus']
    if status != 'Finished':
        return False

    version = sample_info[family_key][family_key]['MIPVersion']
    if not version.startswith('v3.'):
        return False

    return True
