# -*- coding: utf-8 -*-
import logging
import click

from .models import Flowcell
from . import api

log = logging.getLogger(__name__)


@click.command()
@click.option('-l', '--limit', default=10)
@click.argument('flowcell_id', required=False)
@click.pass_context
def show(context, limit, flowcell_id):
    """Show flowcells as JSON objects."""
    if flowcell_id:
        flowcells = Flowcell.query.filter_by(flowcellname=flowcell_id)
    else:
        flowcells = Flowcell.query.limit(limit)
    for flowcell in flowcells:
        click.echo(flowcell.to_json(pretty=True))


@click.command()
@click.option('-e', '--expected', type=int, help='expected number of reads')
@click.option('-d', '--date', is_flag=True, help='show date of last sequencing')
@click.argument('sample_id')
@click.pass_context
def sample(context, expected, date, sample_id):
    """Report how many reads a sample has been sequenced."""
    # fetch sample from the database
    sample_obj = api.get_sample(sample_id)
    # fetch number of reads
    reads = sum(unaligned.readcounts for unaligned in sample_obj.unaligned)
    if expected and reads < expected:
        log.error("not enough reads! ({})".format(reads))
        context.abort()

    if date:
        sorted_dates = sorted(unaligned.demux.flowcell.time for unaligned in
                              sample_obj.unaligned)
        click.echo(sorted_dates[-1])
    else:
        click.echo(reads)
