# -*- coding: utf-8 -*-
import logging

import click
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


def test_analysis(sampleinfo):
    """Test if it's a supported version of MIP."""
    status = sampleinfo['analysisrunstatus']
    if status != 'finished':
        return False

    if not sampleinfo['mip_version'].startswith('v4.'):
        return False

    return True
