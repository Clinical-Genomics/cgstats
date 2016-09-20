# -*- coding: utf-8 -*-
import click

from .models import Flowcell


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
