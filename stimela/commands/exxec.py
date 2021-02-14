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

    recipe_parser.add_argument("recipe-config", help="Recipe configuration file (YAML)")
    recipe_parser.set_defaults(func=exec_recipe)

    for cabname, cab in CONFIG.cab.items():
        cab_parser = parsers.add_parser(cabname, formatter_class=argparse.ArgumentDefaultsHelpFormatter, help=cab.info)

        cabconf = {}
        cabconf['name'] = cabname
        cabconf['opts'] = []

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
            cabconf['opts'].append(name)

        cabconf = OmegaConf.create(cabconf)
        cab_parser.set_defaults(func=exec_cab, cabconf=cabconf)

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

    recipe = OmegaConf.load(args.recipe_config)
    for arg in "indir outdir sid job_type".split():
        if hasattr(args, arg):
            setattr(recipe, arg, getattr(args, arg))
    recipe = OmegaConf.merge(recipe_tmplt, OmegaConf.load(args.recipe_config))


def exec_cab(args, conf):
    log = stimela.logger()
    log.info("exec cab")

    recipe_tmplt = OmegaConf.structured(config.StimelaRecipe)

    ## OMS: I don't understand the point, why not use the original args.cabconf object?
    # cabconf = copy.deepcopy(args.cabconf)
    # del args.cabconf

    recipe = {
        "indir": args.indir,
        "outdir": args.outdir,
        "msdir": args.msdir,
        "info":  f"Running {args.cabconf.name}",
    }

    step = {
        "cab": args.cabconf.name,
        "inputs" : {arg : getattr(args, arg.replace("-", "_")) for arg in args.cabconf.opts}
    }

    recipe['steps'] = {f"step_{args.cabconf.name}" : step}

    recipe = OmegaConf.merge(recipe_tmplt, OmegaConf.create(recipe))

    OmegaConf.update(conf, key='recipe', value=recipe, merge=False)
