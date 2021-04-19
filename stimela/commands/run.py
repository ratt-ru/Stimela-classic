import click
from stimela import config, recipe
from stimela.main import StimelaContext, cli, pass_stimela_context


@cli.command("run", "Run stimela python recipe.", no_args_is_help=True)
@click.argument("script",
                help="Run script")
@click.option("-out", "--outdir", 
                help="Output direcrory")
@click.option("-in", "--indir",
                help="Input folder")
@click.option("-msd", "--msdir",
                help="MS folder. MSs should be placed here. Also, empty MSs will be placed here")
@click.optoin("-g", "--globals", metavar="KEY=VALUE[:TYPE]", action="append", default=[],
                help="Global variables to pass to script. The type is assumed to string unless specified")
def run(context: StimelaContext):

    _globals = dict(_STIMELA_INPUT=args.input, _STIMELA_OUTPUT=args.output,
                    _STIMELA_MSDIR=args.msdir,
                    _STIMELA_JOB_TYPE=args.job_type,
                    _STIMELA_LOG_LEVEL=args.log_level.upper(),
                    _STIMELA_PULLFOLDER=args.pull_folder)

    args.job_type = args.job_type or "docker"
    nargs = len(args.globals)

    global GLOBALS

    if nargs:
        for arg in args.globals:
            if arg.find("=") > 1:
                key, value = arg.split("=")

                try:
                    value, _type = value.split(":")
                except ValueError:
                    _type = "str"

    with open(args.script, 'r') as stdr:
        exec(stdr.read(), _globals)
