from stimela.exceptions import RecipeValidationError, StimelaBaseException
from scabha.exceptions import ScabhaBaseException
from omegaconf.omegaconf import OmegaConf, OmegaConfBaseException
import click
import os.path
from typing import List
from stimela import config
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

    # context.log.info("command-line settings are")
    # print(OmegaConf.to_yaml(settings))

    if os.path.isfile(what):
        context.log.info(f"loading recipe/config {what}")

        # if file contains a recipe entry, treat it as a full config (that can include cabs etc.)
        try:
            conf = OmegaConf.load(what)
            if 'recipe' in conf:
                context.config = config.merge_extra_config(context.config, conf)
            else:
                recipeconf = OmegaConf.structured(Recipe)
                recipeconf = OmegaConf.merge(recipeconf, conf)
                context.config.recipe = recipeconf
        except OmegaConfBaseException as exc:
            context.log.error(f"Error loading {what}: {exc}")
            raise RuntimeError(f"Error loading {what}: {exc}")

        # create recipe object from the config
        recipe = Recipe(**context.config.recipe)

        step = Step(recipe=recipe, info=what, params=params)

    elif what in context.config.cabs:
        cabname = what
        context.log.info(f"setting up cab {cabname}")

        # create step config by merging in settings (var=value pairs from the command line) 
        step = Step(cab=cabname, params=params)

    else:
        context.log.error(f"'{what}' is neither a recipe file nor a known stimela cab")
        return 2 

    retcode = 0
    # finalize
    try:
        step.finalize(context.config)
    except ScabhaBaseException  as exc:
        if not exc.logged:
            context.log.error(f"finalization failed: {exc}")
        return 1

    # pre-validate parameter completeness
    try:
        recipe.prevalidate(params)
    except RecipeValidationError as exc:
        if not exc.logged:
            context.log.error(f"pre-validation failed: {exc}")
        return 1

    context.log.debug("---------- prevalidated step follows ----------")
    for line in step.summary:
        context.log.debug(line)

    try:
        retcode = step.run()
    except ScabhaBaseException as exc:
        if not exc.logged:
            context.log.error(f"run failed with exception: {exc}")
        return 1

    if retcode is not 0:
        context.log.error(f"run failed with error code {retcode}")
        return 1 if retcode is None else retcode

    return retcode
