from stimela import logger, LOG_FILE, BASE, utils, GLOBALS


_loglevels = ["INFO", "DEBUG" ,"ERROR" ]

def make_parser(subparsers):
    parser = subparsers.add_parser("run", help='Run stimela script')

    add = parser.add_argument

    add("-in", "--input",
        help="Input folder")

    add("-out", "--output",
        help="Output folder")

    add("-ms", "--msdir",
        help="MS folder. MSs should be placed here. Also, empty MSs will be placed here")

    add("-pf", "--pull-folder",
        help="Folder to store singularity images.")

    add("script",
        help="Run script")

    add("-g", "--globals", metavar="KEY=VALUE[:TYPE]", action="append", default=[],
        help="Global variables to pass to script. The type is assumed to string unless specified")

    add("-jt", "--job-type", choices=["docker", "singularity", "podman"],
        help="Container technology to use when running jobs")

    add("-ll", "--log-level", default="INFO", choices=_loglevels,
        help="Log level. Set to DEBUG for verbose logging")

    parser.set_defaults(func=run)



def run(args, conf):

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

                GLOBALS[key] = eval("{:s}('{:s}')".format(_type, value))

    utils.CPUS = 1

    with open(args.script, 'r') as stdr:
        exec(stdr.read(), _globals)


