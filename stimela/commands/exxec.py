import stimela
from stimela import Recipe, config
from stimela import logger, LOG_FILE, BASE
import argparse
from omegaconf.omegaconf import OmegaConf
import copy



def make_parser(subparsers):
    """
        subparsers
    """
    from stimela.main import CONFIG

    exec_parser = subparsers.add_parser('exec', help='Run a recipe (YAML) or a stand alone cab')

    parsers = exec_parser.add_subparsers()

    recipe_parser = parsers.add_parser("recipe", formatter_class=argparse.ArgumentDefaultsHelpFormatter, help="Run user-specified recipe")

    recipe_parser.add_argument("recipe_config", help="Recipe configuration file (YAML)")
    recipe_parser.set_defaults(func=exec_recipe)

    for cabname, cab in CONFIG.cab.items():
        cab_parser = parsers.add_parser(cabname, formatter_class=argparse.ArgumentDefaultsHelpFormatter, help=cab.info)

        ## OMS: not really needed, we can pass the cab name via parser.set_defaults, while 'opts'
        ## is surely just the keys of cab.inputs?
        # cabconf = {}
        # cabconf['name'] = cabname
        # cabconf['opts'] = []

        for name, param in cab.inputs.items():
            if param.dtype in ['file', 'File', 'Directory']:
                dtype = str
            elif isinstance(param.dtype, list):
                dtype = str
            ### OMS: temporarily forcing this to str because this looks like a bug
            addopts =  dict(type=str, help=f"{param.info} (type: {param.dtype})")
            if hasattr(param, 'default'):
                addopts['default'] = param['default']
            
            cab_parser.add_argument(f"--{name}", **addopts)

        cab_parser.set_defaults(func=exec_cab, cabname=cabname)

    # these arguments common to reciepes and cabs, so define them at top level
    exec_parser.add_argument("--indir", "-in", 
                    help="Input directory")

    exec_parser.add_argument("--msdir", "-ms", 
                    help="MS directory")

    exec_parser.add_argument("--outdir", "-out", 
                    help="Output directory")

    exec_parser.add_argument("--job-type", "-jt", dest="backend", choices=["docker", 
                        "singularity", "podman"],
                    help="Contairization tool to use")

    exec_parser.add_argument("--singularity-image-dir", "-sid", dest="sid",
                    help="Singularity image directory")


def exec_recipe(args, conf):
    log = stimela.logger()
    log.info("exec recipe")

    recipe = OmegaConf.structured(config.StimelaRecipe)

    # load config file and apply schema
    recipe = OmegaConf.merge(recipe, OmegaConf.load(args.recipe_config))

    # override fields from command line
    for arg in "indir outdir sid job_type".split():
        value = getattr(args, arg, None)
        if value is not None:
            recipe[arg] = value

    print(OmegaConf.to_yaml(conf.recipe))


def exec_cab(args, conf):
    from stimela.main import CONFIG
    log = stimela.logger()

    cabname = args.cabname
    cabconf = CONFIG.cab[cabname]

    log.info(f"exec cab {cabname}")

    ## OMS: note that it's simpler to create a recipe object from the schema, then populate it directly as below
    ## (rather than creating a dict, converting it, then merging it)
    recipe = OmegaConf.structured(config.StimelaRecipe)

    ## OMS: I don't understand the point, why not use the original args.cabconf object? Anyway removed rhe whole cabconf dict, no need for it, see above
    # cabconf = copy.deepcopy(args.cabconf)
    # del args.cabconf

    step = OmegaConf.structured(config.StimelaStep)
    step.cab = cabname
    step.inputs = {arg: getattr(args, arg.replace("-", "_")) for arg in cabconf.inputs}

    recipe.indir    = args.indir
    recipe.outdir   = args.outdir
    recipe.msdir    = args.msdir
    recipe.info     = f"Running {cabname}"
    recipe.steps    = { f"step_{cabname}" : step}

    conf.recipe = recipe

    print(OmegaConf.to_yaml(conf.recipe))
