import click
import os.path
from typing import List
import stimela
from stimela import config
from stimela.main import cli
from omegaconf.omegaconf import OmegaConf
import stimela
from datetime import datetime
from enum import Enum


@cli.command(
    help="""With no arguments, lists stimela configuration settings. With KEY=VALUE arguments, changes the configuration file.
            Default is to change whichever configuration file was loaded (local, virtual env, or user-level).
            """,
    short_help="manipulate configuration settings")
@click.argument("settings", nargs=-1, metavar="KEY=VALUE", required=False) 
@click.option("--local", "-l", "save", flag_value='local', 
                help="Save config file locally.")
@click.option("--virtual-env", "-v", "save", flag_value='venv', 
                help="Save config file at the virtual environment level.")
@click.option("--user", "-u", "save", flag_value='user', 
                help="Save config file at the user level.")
def config(settings, save=None):
    log = stimela.logger()
    from stimela import CONFIG
    from stimela.config import CONFIG_LOADED, CONFIG_LOCATIONS

    if CONFIG_LOADED:
        log.info(f"configuration loaded from {CONFIG_LOADED}")
    else:
        log.info(f"no configuration files found, using built-in defaults")

    # print config, if no key=value args specified
    if not settings:
        for key, value in context.config.opts.items():
            if isinstance(value, Enum):
                value = value.name
            print(f"    {key} = {value}")

    # change config, if key=value args specified
    for keyvalue in settings:
        if "=" not in keyvalue:
            log.error(f"invalid config setting '{keyvalue}', KEY=VALUE expected")
            return 2
        key, value = keyvalue.split("=", 1)
        if key not in CONFIG.opts:
            log.error(f"unknown config key '{key}'")
            return 2
        CONFIG.opts[key] = value
        print(f"    setting {key} = {value}")

    # save config if changed, or --save given
    if settings or save:
        if save is None:
            output_config = CONFIG_LOADED or CONFIG_LOCATIONS['user']
        else:
            output_config = CONFIG_LOCATIONS[save]
            if not output_config:
                log.error(f"can't write config file at the {save} level")
                return 2
        with open(output_config, "wt") as fp:
            fp.write(f"## Stimela {stimela.__version__} configuration file\n")
            fp.write(f"## Saved on {datetime.now().ctime()}\n\n")
            OmegaConf.save(config=CONFIG.opts, f=fp)
        log.info(f"wrote configuration to {output_config}")
                