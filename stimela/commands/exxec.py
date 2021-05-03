from stimela import configuratt
from stimela.exceptions import RecipeValidationError, StimelaBaseException
from scabha.exceptions import ScabhaBaseException
from omegaconf.omegaconf import OmegaConf, OmegaConfBaseException
import click
import logging
import os.path
from typing import List
import stimela
from stimela import config, logger
from stimela.main import StimelaContext, cli, pass_stimela_context

from stimela.kitchen.recipe import Recipe, Step



@cli.command("exec",
    help="Execute a single cab, or a YML recipe. Use KEY=VALUE to specify"\
    " parameters and settings for the cab or recipe",
    short_help="execute a cab or a YML recipe",
    no_args_is_help=True)
@click.argument("what", metavar="RECIPE.yml|CAB") 
@click.argument("params", nargs=-1, metavar="KEY=VALUE", required=False) 
@pass_stimela_context
def exxec(context: StimelaContext, what: str, params: List[str] = []):

    invalid = [p for p in params if "=" not in p]
    if invalid:
        context.log.error(f"invalid parameters: {' '.join(invalid)}")
        return 2
    
    params = dict(p.split("=", 1) for p in params if "=" in p)

    log = logger()

    if os.path.isfile(what):
        log.info(f"loading recipe/config {what}")

        # if file contains a recipe entry, treat it as a full config (that can include cabs etc.)
        try:
            conf = configuratt.load_using(what, stimela.CONFIG)
            if 'recipe' in conf:
                stimela.CONFIG = config.merge_extra_config(stimela.CONFIG, conf)
            else:
                recipeconf = OmegaConf.structured(Recipe)
                recipeconf = OmegaConf.merge(recipeconf, conf)
                stimela.CONFIG.recipe = recipeconf
        except OmegaConfBaseException as exc:
            log.error(f"Error loading {what}: {exc}")
            return 2

        # create recipe object from the config, wrapped in a step
        step = Step(recipe=Recipe(**stimela.CONFIG.recipe), info=what, params=params)

    elif what in context.config.cabs:
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
