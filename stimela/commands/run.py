import click
from stimela import config, recipe, GLOBALS
from stimela.main import StimelaContext, cli, pass_stimela_context
from typing import Optional, List


@cli.command("run", help="Run stimela python recipe.", no_args_is_help=True)
@click.argument("script")
@click.option("-out", "--outdir", 
                help="Output direcrory")
@click.option("-in", "--indir",
                help="Input folder")
@click.option("-msd", "--msdir",
                help="MS folder. MSs should be placed here. Also, empty MSs will be placed here")
@click.option("-g", "--globals", "myglobals", metavar="KEY=VALUE[:TYPE]", multiple=True,
                help="Global variables to pass to script. The type is assumed to string unless specified")
@pass_stimela_context
def run(context: StimelaContext, script: str, outdir: str=None, 
        indir: str=None, msdir: str=None, myglobals: List[str]=[]):
    
    global GLOBALS
    _globals = dict(_STIMELA_INPUT=indir, _STIMELA_OUTPUT=outdir,
                    _STIMELA_MSDIR=msdir)
    
    args.job_type = args.job_type or "docker"
    nargs = len(myglobals)

    if nargs:
        for arg in myglobals:
            if arg.find("=") > 1:
                key, value = arg.split("=")

                try:
                    value, _type = value.split(":")
                except ValueError:
                    _type = "str"

    with open(script, 'r') as stdr:
        exec(stdr.read(), _globals)
