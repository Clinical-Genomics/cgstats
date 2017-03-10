# -*- coding: utf-8 -*-
import logging

import click

log = logging.getLogger(__name__)


@click.command()
@click.option('-r', '--reset', is_flag=True)
@click.pass_context
def init(context, reset):
    """Setup the clinstats database."""
    manager = context.obj['manager']
    if reset:
        manager.drop_all()
    manager.create_all()
