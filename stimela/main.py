# -*- coding: future_fstrings -*-
import os
import click
import textwrap as _textwrap
import stimela
from stimela.utils import logger
from stimela.cargo import cab
from stimela import config
from dataclasses import dataclass

BASE = stimela.BASE
CAB = stimela.CAB
USER = stimela.USER
UID = stimela.UID
GID = stimela.GID
LOG_HOME = stimela.LOG_HOME
LOG_FILE = stimela.LOG_FILE
GLOBALS = stimela.GLOBALS
CAB_USERNAME = stimela.CAB_USERNAME

log = None
CONFIG = None

def get_cabs(logfile):
    log = logger.StimelaLogger(logfile)
    cabs_ = log.read()['images']

    # Remove images that are not cabs
    keys = list(cabs_.keys())
    for key in keys:
        if not cabs_[key]['CAB']:
            del cabs_[key]

    return cabs_


def get_cab_definition(cabdir, header=False, display=True):
    """ prints out help information about a cab """

    # First check if cab exists
    pfile = "{}/parameters.json".format(cabdir)
    if not os.path.exists(pfile):
        raise RuntimeError("Cab could not be found at : {}".format(cabdir))
    # Get cab info
    cab_definition = cab.CabDefinition(parameter_file=pfile)
    if display:
        cab_definition.display(header)

    return cab_definition


## this class is passed to subcommands (instead of having them rely on importing globals)
@dataclass 
class StimelaContext(object):
    config  : object
    log     : object
    backend : object

pass_stimela_context = click.make_pass_decorator(StimelaContext)


@click.group()
@click.option('--backend', '-b', type=click.Choice(config.Backend._member_names_), 
                help="Backend to use (for containerization).")
@click.version_option(str(stimela.__version__))
@click.pass_context
def cli(ctx, backend):
    global log
    log = stimela.logger()
    log.info(f"starting")        # remove this eventually, but it's handy for timing things right now

    # load config files
    global CONFIG
    CONFIG = config.load_config()
    if config.CONFIG_LOADED:
        log.info(f"loaded config from {config.CONFIG_LOADED}") 

    # set backend module
    global BACKEND 
    if backend:
        CONFIG.opts.backend = backend
    BACKEND = getattr(stimela.backends, CONFIG.opts.backend.name)
    log.info(f"backend is {CONFIG.opts.backend.name}")

    # create context to be passed to commands
    ctx.obj = StimelaContext(CONFIG, log, BACKEND)


# import commands
from stimela.commands import exxec, images, build, push, save_config

def main():
    cli()

## the ones not listed above haven't been converted to click yet. They are:
# cabs, clean, containers, kill, ps, pull, run
