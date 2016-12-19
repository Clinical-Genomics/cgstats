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
    query = api.get_sample(sample_id)
    num_samples = query.count()
    if num_samples == 0:
        click.echo("sample not found in database")
        context.abort()
    elif num_samples > 1:
        samples_str = ", ".join(sample.samplename for sample in query)
        click.echo("conflicting samples: {}".format(samples_str))
        context.abort()
    else:
        sample_obj = query.one()

    # fetch number of reads
    reads = sum(unaligned.readcounts for unaligned in sample_obj.unaligned)
    if expected and reads < expected:
        log.error("not enough reads! ({})".format(reads))
        context.abort()

    if date:
        sorted_dates = sorted(unaligned.demux.datasource.rundate for unaligned
                              in sample_obj.unaligned)
        click.echo(sorted_dates[-1])
    else:
        click.echo(reads)


@click.command()
@click.option('-l', '--limit', default=20, help='limit number of flowcells')
@click.option('-o', '--offset', default=0, help='skip initial flowcells')
@click.option('-s', '--sample', help='look up flowcells based on sample')
@click.pass_context
def flowcells(context, limit, offset, sample):
    """Get information about flowcells."""
    query = api.flowcells(sample=sample)
    for flowcell in query.offset(offset).limit(limit):
        click.echo(flowcell.flowcellname)


@click.command()
@click.option('-l', '--limit', default=20, help='limit number of flowcells')
@click.option('-o', '--offset', default=0, help='skip initial flowcells')
@click.option('-f', '--flowcell', help='flowcell name')
@click.pass_context
def samples(context, limit, offset, flowcell):
    """List samples in the database."""
    query = api.samples(flowcell_name=flowcell)
    for sample in query.offset(offset).limit(limit):
        click.echo(sample.lims_id)
