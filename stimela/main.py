# -*- coding: future_fstrings -*-
import os, logging, re, time
import click
import stimela
from omegaconf import OmegaConf
from stimela import config, stimelogging
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

@click.group()
@click.option('--backend', '-b', type=click.Choice(config.Backend._member_names_), 
                help="Backend to use (for containerization).")
@click.option('--config', '-c', 'config_files', metavar='FILE', multiple=True,
                help="Extra config file(s) to load. Prefix with '=' to override standard config files.")
@click.option('--verbose', '-v', is_flag=True, help='Be extra verbose in output.')
@click.version_option(str(stimela.__version__))
def cli(backend, config_files=[], verbose=False):
    global log
    log = stimela.logger(loglevel=logging.DEBUG if verbose else logging.INFO)
    log.info(f"starting")        # remove this eventually, but it's handy for timing things right now

    if verbose:
        log.debug("verbose output enabled")

    # use this logger for exceptions
    import scabha.exceptions
    scabha.exceptions.set_logger(log)

    # load config files
    stimela.CONFIG = config.load_config(extra_configs=config_files)
    if config.CONFIG_LOADED:
        log.info(f"loaded config from {config.CONFIG_LOADED}") 

    # enable logfiles and such
    if stimela.CONFIG.opts.log.enable:
        if verbose:
            stimela.CONFIG.opts.log.level = "DEBUG"
        # setup file logging
        stimelogging.update_file_logger(log, stimela.CONFIG.opts.log.name, subst=dict(name="stimela"))

    # set backend module
    global BACKEND 
    if backend:
        stimela.CONFIG.opts.backend = backend
    BACKEND = getattr(stimela.backends, stimela.CONFIG.opts.backend.name)
    log.info(f"backend is {stimela.CONFIG.opts.backend.name}")



# import commands
from stimela.commands import exxec, images, build, push, run, save_config

## the ones not listed above haven't been converted to click yet. They are:
# cabs, clean, containers, kill, ps, pull, run
