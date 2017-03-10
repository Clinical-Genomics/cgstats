# -*- coding: utf-8 -*-
import codecs
import logging
import os
import pkg_resources

import click
import yaml

from cgstats import __title__, __version__
from cgstats.db import api

log = logging.getLogger(__name__)


def init_log(logger, filename=None, loglevel=None):
    """Initializes the log file in the proper format.

    Args:
        filename (Optional[path]): default is no logging to file
        loglevel (Optional[str]): determine the level of log output
    """
    template = "[%(asctime)s] %(levelname)-8s: %(name)-25s: %(message)s"
    formatter = logging.Formatter(template)

    if loglevel:
        logger.setLevel(getattr(logging, loglevel))

    # We will always print warnings and higher to stderr
    console = logging.StreamHandler()
    console.setLevel('WARNING')
    console.setFormatter(formatter)

    if filename:
        file_handler = logging.FileHandler(filename, encoding='utf-8')
        if loglevel:
            file_handler.setLevel(getattr(logging, loglevel))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    # If no logfile is provided we print all log messages that the user has
    # defined to stderr
    else:
        if loglevel:
            console.setLevel(getattr(logging, loglevel))

    logger.addHandler(console)


class EntryPointsCLI(click.MultiCommand):
    """Add subcommands dynamically to a CLI via entry points."""

    def _iter_commands(self):
        """Iterate over all subcommands as defined by the entry point."""
        subcommands_ep = "{}.subcommands.1".format(__title__)
        return {entry_point.name: entry_point for entry_point in
                pkg_resources.iter_entry_points(subcommands_ep)}

    def list_commands(self, ctx):
        """List the available commands."""
        commands = self._iter_commands()
        return commands.keys()

    def get_command(self, ctx, name):
        """Load one of the available commands."""
        commands = self._iter_commands()
        if name not in commands:
            click.echo("no such command: {}".format(name))
            ctx.abort()
        return commands[name].load()


@click.group(cls=EntryPointsCLI)
@click.option('-c', '--config', default='~/.cgstats.yaml',
              type=click.Path(), help='path to config file')
@click.option('-d', '--database', help='path/URI of the SQL database')
@click.option('-l', '--log-level', default='INFO', help='level to log at')
@click.option('-r', '--reset', is_flag=True,
              help='reset database from scratch')
@click.option('--log-file', type=click.Path(), help='write logs to a file')
@click.version_option(__version__, prog_name=__title__)
@click.pass_context
def root(context, config, database, reset, log_level, log_file):
    """Interact with command line interface."""
    init_log(logging.getLogger(), loglevel=log_level, filename=log_file)
    log.debug("{}: version {}".format(__title__, __version__))
    # read in config file if it exists
    if os.path.exists(config):
        with codecs.open(config) as conf_handle:
            context.obj = yaml.load(conf_handle)
    else:
        context.obj = {}

    if database:
        context.obj['database'] = database
    if context.obj.get('database'):
        context.obj['manager'] = api.connect(context.obj['database'])
