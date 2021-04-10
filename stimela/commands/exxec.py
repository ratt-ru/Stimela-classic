from omegaconf.omegaconf import OmegaConf, OmegaConfBaseException
import click
import os.path
from typing import List
from stimela import config, recipe
from stimela.main import StimelaContext, cli, pass_stimela_context

from stimela.recipe import Step, Recipe



@cli.command("exec",
    help="Execute a single cab, or a YML recipe. Use KEY=VALUE to specify"\
    " parameters and settings for the cab or recipe",
    short_help="execute a cab or a YML recipe",
    no_args_is_help=True)
@click.argument("what", metavar="RECIPE.yml|CAB") 
@click.argument("params", nargs=-1, metavar="KEY=VALUE", required=False) 
@pass_stimela_context
def exxec(context: StimelaContext, what: str, params: List[str] = []):

    params = OmegaConf.from_dotlist(params)
    # context.log.info("command-line settings are")
    # print(OmegaConf.to_yaml(settings))

    if os.path.isfile(what):
        context.log.info(f"loading recipe/config {what}")

        # if file contains a recipe entry, treat it as a full config (that can include cabs etc.)
        try:
            conf = OmegaConf.load(what)
            if 'recipe' in conf:
                context.config = OmegaConf.merge(context.config, conf)
            else:
                recipeconf = OmegaConf.structured(Recipe)
                recipeconf = OmegaConf.merge(recipeconf, conf)
                context.config.recipe = recipeconf
        except OmegaConfBaseException as exc:
            context.log.error(f"Error loading {what}: {exc}")
            raise RuntimeError(f"Error loading {what}: {exc}")

        # create recipe object from the config
        recipe = Recipe(**context.config.recipe)

        # feed in parameters and validate completeness
        recipe.validate(context.config, params)
    
    elif what in context.config.cabs:
        cabname = what
        context.log.info(f"setting up cab {cabname}")

        # create step config by merging in settings (var=value pairs from the command line) 
        step = Step(cab=cabname, params=params)

        # create single-step recipe
        recipe = Recipe(info=f"Running {cabname}")
        recipe.add(step)

        # validate completeness
        recipe.validate(context.config)

        # insert into config
        context.config.recipe = OmegaConf.structured(recipe)

    else:
        context.log.error(f"'{what}' is neither a recipe file nor a known stimela cab")
        return 2 

    print(OmegaConf.to_yaml(context.config.recipe))

    context.log.info("IGNORE SUBSTITUTIONS FOR NOW AS THEY ARE NOT YET IMPLEMENTED")
    for line in recipe.summary:
        context.log.info(line)

