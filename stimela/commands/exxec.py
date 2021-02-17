from omegaconf.omegaconf import OmegaConf
import click
import os.path
from typing import List
from stimela import config
from stimela.main import StimelaContext, cli, pass_stimela_context


@cli.command("exec",
    help="Execute a single cab, or a YML recipe. Use KEY=VALUE to specify"\
    " parameters and settings for the cab or recipe",
    short_help="execute a cab or a YML recipe",
    no_args_is_help=True)
@click.argument("what", metavar="RECIPE.yml|CAB") 
@click.argument("settings", nargs=-1, metavar="KEY=VALUE", required=False) 
@pass_stimela_context
def exxec(context: StimelaContext, what: str, settings: List[str] = []):

    settings = OmegaConf.from_dotlist(settings)
    # context.log.info("command-line settings are")
    # print(OmegaConf.to_yaml(settings))

    if os.path.isfile(what):
        context.log.info(f"loading recipe {what}")
        recipe = OmegaConf.structured(config.StimelaRecipe)
        recipe = OmegaConf.merge(recipe, OmegaConf.load(what), settings)
    
    elif what in context.config.cab:
        cabname = what
        context.log.info(f"setting up cab {cabname}")

        recipe = OmegaConf.structured(config.StimelaRecipe)
        step = OmegaConf.structured(config.StimelaStep)

        step.cab = cabname
        step = OmegaConf.merge(step, settings)

        ## OMS: propose to replace these with recipe.dir.input, recipe.dir.output, etc.
        # recipe.indir    = args.indir
        # recipe.outdir   = args.outdir
        # recipe.msdir    = args.msdir
        recipe.info     = f"Running {cabname}"
        recipe.steps    = {f"step_{cabname}" : step}

    else:
        context.log.error(f"'{what}' is neither a recipe file nor a known stimela cab")
        return 2 

    context.config.recipe = recipe
    print(OmegaConf.to_yaml(context.config.recipe))
