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

    configs = config.load_config()

    exec_parser = subparsers.add_parser('exec', help='Run a recipe (YAML) or a stand alone cab')

    parsers = exec_parser.add_subparsers()

    iters = ["recipe"] + list(configs.cab)
    for cabname in iters:
        if cabname == "recipe":
            parser = parsers.add_parser(cabname, formatter_class=argparse.ArgumentDefaultsHelpFormatter, help="User specified recipe")

            parser.add_argument("--recipe-config", "-rc",
                            help="Recipe configuration file (YAML)")
            parser.set_defaults(func=addtoconf)
        else:


            cab = getattr(configs.cab, cabname)
            parser = parsers.add_parser(cabname, formatter_class=argparse.ArgumentDefaultsHelpFormatter, help=cab.info)


            cabconf = {}
            cabconf['name'] = cabname
            cabconf['opts'] = []

            for name, param in cab.inputs.items():
                if param.dtype in ['file', 'File', 'Directory']:
                    dtype = str
                elif isinstance(param.dtype, list):
                    dtype = str
                
                addopts =  dict(type=dtype, help=f"{param.info} (type: {param.dtype})")
                if hasattr(param, 'default'):
                    addopts['default'] = param['default']
                
                parser.add_argument(f"--{name}", **addopts)
                cabconf['opts'].append(name)

            cabconf = OmegaConf.create(cabconf)
            parser.set_defaults(func=addtoconf, cabconf=cabconf)

        parser.add_argument("--indir", "-in", 
                        help="Input directory")

        parser.add_argument("--msdir", "-ms", 
                        help="MS directory")

        parser.add_argument("--outdir", "-out", 
                        help="Output directory")

        parser.add_argument("--job-type", "-jt", dest="backend", choices=["docker", 
                            "singularity", "podman"],
                        help="Contairization tool to use")

        parser.add_argument("--singularity-image-dir", "-sid", dest="sid",
                        help="Singularity image directory")


def addtoconf(args, conf):
    """ 
        args

        conf
    """

    recipe_tmplt = OmegaConf.structured(config.StimelaRecipe)

    if args.recipe_config is not None:
        recipe = OmegaConf.load(args.recipe_config)
        for arg in "indir outdir sid job_type".split():
            if hasattr(args, arg):
                setattr(recipe, arg, getattr(args, arg))
        recipe = OmegaConf.merge(recipe_tmplt, OmegaConf.load(args.recipe_config))

    else:
        cabconf = copy.deepcopy(args.cabconf)
        del args.cabconf
        recipe = {
            "indir": args.indir,
            "outdir": args.outdir,
            "msdir": args.msdir,
            "info":  f"Running {cabconf.name}",
        }

        step = {
            "cab": cabconf.name,
            "inputs" : {arg : getattr(args, arg) for arg in cabconf.opts}
        }

        recipe['steps'] = {f"step_{cabconf.name}" : step}

        recipe = OmegaConf.merge(recipe_tmplt, OmegaConf.create(recipe))

    OmegaConf.update(conf, key='recipe', value=recipe, merge=False)
