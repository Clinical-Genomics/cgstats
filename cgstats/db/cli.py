# -*- coding: utf-8 -*-
import logging
import click
from path import Path
from glob import glob

from .models import Flowcell, Version, Sample, Demux, Unaligned
from . import api
from . import xparse
from . import parse

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
@click.option('-v', '--verbose', is_flag=True, help='show more information')
@click.pass_context
def flowcells(context, limit, offset, sample, verbose):
    """Get information about flowcells."""
    query = api.flowcells(sample=sample)
    for flowcell in query.offset(offset).limit(limit):
        if verbose:
            click.echo(flowcell.to_json(pretty=True))
        else:
            click.echo(flowcell.flowcellname)


@click.command()
@click.option('-l', '--limit', default=20, help='limit number of flowcells')
@click.option('-o', '--offset', default=0, help='skip initial flowcells')
@click.option('-f', '--flowcell', help='flowcell name')
@click.pass_context
def samples(context, limit, offset, flowcell):
    """List samples in the database."""
    query = api.samples(flowcell_name=flowcell)
    if flowcell is None:
        query = query.offset(offset).limit(limit)
    for sample in query:
        click.echo(sample.lims_id)


@click.command()
@click.argument('flowcell')
@click.option('-p', '--project', help='project name')
@click.pass_context
def select(context, flowcell, project):
    """List samples in the database."""
    query = api.select(flowcell, project)

    click.echo("sample\tFlowcell\tLanes\treadcounts/lane\tsum_readcounts\tyieldMB/lane\tsum_yield\t%Q30\tMeanQscore")
    for line in query:
        click.echo('\t'.join( str(s) for s in [line.samplename, line.flowcellname, line.lanes, line.reads, line.readsum, line.yld, line.yieldsum, line.q30, line.meanq] ))


@click.command()
@click.argument('demux_dir')
@click.option('-m', '--machine', type=click.Choice(['X', '2500']), help='machine type')
@click.option('-u', '--unaligned', help='the unaligned dir name')
@click.option('-a', '--all-unaligned', is_flag=True, help='add all Unaligned* dirs')
@click.pass_context
def add(context, machine, demux_dir, unaligned, all_unaligned):
    """Add a FC to cgstats."""

    #if not Version.check(config['clinstats']['name'], config['clinstats']['version']):
    #    logger.error('Wrong database!')
    #    exit(1) # change to exception

    manager = context.obj['manager']

    if machine == 'X':
        xparse.add(manager, demux_dir)
    if machine == '2500':
        if all_unaligned:
            unaligned_dirs = glob(Path(demux_dir).joinpath('Unaligned*'))
            for unaligned in unaligned_dirs:
                log.info('Adding {}.'.format(unaligned))
                parse.add(manager, demux_dir, unaligned)
        else:
            log.info('Adding {}.'.format(unaligned))
            parse.add(manager, demux_dir, unaligned)

@click.command()
@click.option('-f', '--flowcell', help='flowcell to remove')
@click.option('-b', '--basemask', help='demux with given basemask to remove')
@click.option('-s', '--sample', help='sample to remove')
@click.pass_context
def delete(context, flowcell, basemask, sample):

    if flowcell:
        rs = Flowcell.query.filter_by(flowcellname=flowcell)

    if basemask:
        if not flowcell:
            click.echo('Missing flowcell parameter', err=True)
            context.abort()
        rs = Demux.query.filter_by(basemask=basemask)

    if sample:
        rs = Sample.query.filter_by(limsid=sample)
        if flowcell:
            rs = rs.join(Unaligned).join(Demux).join(Flowcell).filter_by(flowcellname=flowcell)

    rs = rs.all()
    manager = context.obj['manager']
    if click.confirm("Are you sure you want to delete {}?".format(rs)):
        manager.delete(rs)
        manager.commit()
