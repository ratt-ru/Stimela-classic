import dataclasses
from stimela import configuratt
from scabha.exceptions import ScabhaBaseException
from omegaconf.omegaconf import OmegaConf, OmegaConfBaseException
import click
import logging
import os.path
from typing import List, Optional
import stimela
from stimela import logger
from stimela.main import cli
from stimela.kitchen.recipe import Recipe, Step, join_quote
from stimela.config import get_config_class


@cli.command("exec",
    help="Execute a single cab, or a YML recipe. Use KEY=VALUE to specify"\
    " parameters and settings for the cab or recipe",
    short_help="execute a cab or a YML recipe",
    no_args_is_help=True)
@click.option("-r", "--recipe", "recipe_name", default="recipe", metavar="SECTION",
                help="selects recipe to run from YML file, default is 'recipe'")
@click.argument("what", metavar="RECIPE.yml|CAB") 
@click.argument("params", nargs=-1, metavar="KEY=VALUE", required=False) 
def exxec(what: str, params: List[str] = [], recipe_name: str = "recipe"):

    log = logger()
    invalid = [p for p in params if "=" not in p]
    if invalid:
        log.error(f"invalid parameters: {' '.join(invalid)}")
        return 2
    
    params = dict(p.split("=", 1) for p in params if "=" in p)

    if os.path.isfile(what):
        log.info(f"loading recipe/config {what}")

        # if file contains a recipe entry, treat it as a full config (that can include cabs etc.)
        try:
            conf = configuratt.load_using(what, stimela.CONFIG)
        except OmegaConfBaseException as exc:
            log.error(f"Error loading {what}: {exc}")
            return 2

        # anything that is not a standard config section will be treated as a recipe
        all_recipe_names = [name for name in conf if name not in stimela.CONFIG]
        log.info(f"{what} contains the following recipe sections: {join_quote(all_recipe_names)}")

        if recipe_name not in conf:
            log.error(f"{what} does not contain a '{recipe_name}' section")
            return 2
        if recipe_name in stimela.CONFIG:
            log.error(f"'{recipe_name}' is not a valid recipe name")
            return 2
        
        # merge into config, treating each section as a recipe
        config_fields = []
        for section in conf:
            if section not in stimela.CONFIG:
                config_fields.append((section, Optional[Recipe], dataclasses.field(default=None)))
        dcls = dataclasses.make_dataclass("UpdatedStimelaConfig", config_fields, bases=(get_config_class(),)) 
        config_schema = OmegaConf.structured(dcls)

        try:
            stimela.CONFIG = OmegaConf.merge(stimela.CONFIG, config_schema, conf)
        except OmegaConfBaseException as exc:
            log.error(f"Error loading {what}: {exc}")
            return 2

        log.info(f"selected recipe is '{recipe_name}'")

        # create recipe object from the config, wrapped in a step
        step = Step(recipe=Recipe(**stimela.CONFIG[recipe_name]), info=what, params=params)

    elif what in stimela.CONFIG.cabs:
        cabname = what
        log.info(f"setting up cab {cabname}")

        # create step config by merging in settings (var=value pairs from the command line) 
        step = Step(cab=cabname, params=params)

    else:
        log.error(f"'{what}' is neither a recipe file nor a known stimela cab")
        return 2 

    # prevalidate() is done by run() automatically if not already done, so we only need this in debug mode, so that we
    # can pretty-print the recipe
    if log.isEnabledFor(logging.DEBUG):
        try:
            step.prevalidate()
        except ScabhaBaseException as exc:
            if not exc.logged:
                log.error(f"pre-validation failed: {exc}")
            return 1

        log.debug("---------- prevalidated step follows ----------")
        for line in step.summary:
            log.debug(line)

    # run step

    try:
        outputs = step.run()
    except ScabhaBaseException as exc:
        if not exc.logged:
            log.error(f"run failed with exception: {exc}")
        return 1

    if outputs:
        log.info("run successful, outputs follow:")
        for name, value in outputs.items():
            log.info(f"  {name}: {value}")
    else:
        log.info("run successful")


    return 0
