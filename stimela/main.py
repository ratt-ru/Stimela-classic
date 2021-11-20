# -*- coding: future_fstrings -*-
import os
import argparse
from argparse import ArgumentParser
import textwrap as _textwrap
import signal
import stimela
from stimela import docker, singularity, podman, utils
from stimela.utils import logger
from stimela.cargo import cab

BASE = stimela.BASE
CAB = stimela.CAB
USER = stimela.USER
UID = stimela.UID
GID = stimela.GID
GLOBALS = stimela.GLOBALS
CAB_USERNAME = stimela.CAB_USERNAME

loglevels = "info debug error"

class MultilineFormatter(argparse.HelpFormatter):
    def _fill_text(self, text, width, indent):
        text = self._whitespace_matcher.sub(' ', text).strip()
        paragraphs = text.split('|n ')
        multiline_text = ''
        for paragraph in paragraphs:
            formatted_paragraph = _textwrap.fill(
                paragraph, width, initial_indent=indent, subsequent_indent=indent) + '\n\n'
            multiline_text = multiline_text + formatted_paragraph
        return multiline_text

def build(argv):
    for i, arg in enumerate(argv):
        if (arg[0] == '-') and arg[1].isdigit():
            argv = ' ' + arg
    
    parser = ArgumentParser(description='Build executor (a.k.a cab) images')
    parser.add_argument("-b", "--base", action="store_true",
                        help="Build base images")

    parser.add_argument("-c", "--cab", metavar="CAB,CAB_DIR",
                        help="Executor image (name) name, location of executor image files")

    parser.add_argument("-uo", "--us-only",
                        help="Only build these cabs. Comma separated cab names")

    parser.add_argument("-i", "--ignore-cabs", default="",
                        help="Comma separated cabs (executor images) to ignore.")
    
    parser.add_argument("-p", "--podman", action="store_true",
        help="Build images using podman.")

    parser.add_argument("-nc", "--no-cache", action="store_true",
                        help="Do not use cache when building the image")


    jtype = "podman" if podman else "docker"
    args = parser.parse_args(argv)

    no_cache = ["--no-cache"] if args.no_cache else []

    if args.cab:
        raise SystemExit("DEPRECATION NOTICE: This feature has been deprecated. Please specify your \
                custom cab via the 'cabpath' option of the Recipe.add() function.")

    if args.base:
        # Build base and meqtrees images first
        BASE.remove("base")
        BASE.remove("meqtrees")
        BASE.remove("casa")
        BASE.remove("astropy")

        for image in ["base", "meqtrees", "casa", "astropy"] + BASE:
            dockerfile = "{:s}/{:s}".format(stimela.BASE_PATH, image)
            image = "stimela/{0}:{1}".format(image, stimela.__version__)
            #__call__(jtype).build(image,
            #             dockerfile, args=no_cache)

        return 0
    raise SystemExit("DEPRECATION NOTICE: The building of cab images has been deprecated")


def info(cabdir, header=False, display=True):
    """ prints out help information about a cab """

    # First check if cab exists
    pfile = "{}/parameters.json".format(cabdir)
    if not os.path.exists(pfile):
        raise RuntimeError("Cab could not be found at : {}".format(cabdir))
    # Get cab info
    cab_definition = cab.CabDefinition(parameter_file=pfile)
    if display:
        cab_definition.display(header)

    return cab_definition


def cabs(argv):
    for i, arg in enumerate(argv):
        if (arg[0] == '-') and arg[1].isdigit():
            argv = ' ' + arg

    parser = ArgumentParser(description='List executor (a.k.a cab) images')
    parser.add_argument("-i", "--cab-doc",
                        help="Will display document about the specified cab. For example, \
to get help on the 'cleanmask cab' run 'stimela cabs --cab-doc cleanmask'")

    parser.add_argument("-l", "--list", action="store_true",
                        help="List cab names")

    parser.add_argument("-ls", "--list-summary", action="store_true",
                        help="List cabs with a summary of the cab")

    args = parser.parse_args(argv)

    if args.cab_doc:
        name = '{0:s}_cab/{1:s}'.format(CAB_USERNAME, args.cab_doc)
        cabdir = "{:s}/{:s}".format(stimela.CAB_PATH, args.cab_doc)
        info(cabdir)

    elif args.list_summary:
        for val in CAB:
            cabdir = "{:s}/{:s}".format(stimela.CAB_PATH, val)
            try:
                info(cabdir, header=True)
            except IOError:
                pass
    else:
        print(', '.join(CAB))


def run(argv):
    for i, arg in enumerate(argv):
        if (arg[0] == '-') and arg[1].isdigit():
            argv[i] = ' ' + arg

    parser = ArgumentParser(description='Dockerized Radio Interferometric Scripting Framework.\n'
                                        'Sphesihle Makhathini <sphemakh@gmail.com>')

    add = parser.add_argument

    add("-r", "--repository", default="quay.io",
        help="Repository from which to pull docker images. The default repository is quay.io")

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

    add("-ll", "--log-level", default="INFO", choices=loglevels.upper().split() + loglevels.split(),
        help="Log level. set to DEBUG/debug for verbose logging")

    args = parser.parse_args(argv)

    _globals = dict(_STIMELA_INPUT=args.input, _STIMELA_OUTPUT=args.output,
                    _STIMELA_MSDIR=args.msdir,
                    _STIMELA_JOB_TYPE=args.job_type,
                    _STIMELA_REP=args.repository,
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


def pull(argv):
    for i, arg in enumerate(argv):
        if (arg[0] == '-') and arg[1].isdigit():
            argv[i] = ' ' + arg

    parser = ArgumentParser(description='Pull docker stimela base images')

    add = parser.add_argument

    add("-r", "--repository", default="quay.io",
        help="Repository from which to pull docker images. The default repository is quay.io")
        
    add("-im", "--image", nargs="+", metavar="IMAGE[:TAG]",
        help="Pull base image along with its tag (or version). Can be called multiple times")

    add("-f", "--force", action="store_true",
        help="force pull if image already exists")

    add("-s", "--singularity", action="store_true",
        help="Pull base images using singularity."
        "Images will be pulled into the directory specified by the enviroment varaible, STIMELA_PULLFOLDER. $PWD by default")

    add("-d", "--docker", action="store_true",
        help="Pull base images using docker.")

    add("-p", "--podman", action="store_true",
        help="Pull base images using podman.")

    add("-cb", "--cab-base", nargs="+",
        help="Pull base image for specified cab")

    add("-pf", "--pull-folder",
        help="Images will be placed in this folder. Else, if the environmnental variable 'STIMELA_PULLFOLDER' is set, then images will be placed there. "
        "Else, images will be placed in the current directory")

    args = parser.parse_args(argv)

    if args.pull_folder:
        pull_folder = args.pull_folder
    else:
        try:
            pull_folder = os.environ["STIMELA_PULLFOLDER"]
        except KeyError:
            pull_folder = "."

    if args.podman:
        jtype = "podman"
    elif args.singularity:
        jtype = "singularity"
    elif args.docker:
        jtype = "docker"
    else:
        jtype = "docker"

    images_ = []
    repository_ = []
    for cab in args.cab_base or []:
        if cab in CAB:
            filename = "/".join([stimela.CAB_PATH, cab, "parameters.json"])
            param = utils.readJson(filename)
            tags = param["tag"]
            if not isinstance(tags, list):
                tags = [tags]
            for tag in tags:
                images_.append(":".join([param["base"], tag]))
                repository_.append(param["hub"] if "hub" in param.keys() else args.repository)

    repository_ = repository_ + ([args.repository] * len(args.image) if args.image is not None else [])
    args.image = images_ + (args.image if args.image is not None else [])
    assert len(args.image) == len(repository_)
    if args.image:
        for hub, image in zip(repository_, args.image):
            if hub == "docker" or hub == "docker.io":
                hub = ""
            if args.singularity:
                simage = image.replace("/", "_")
                simage = simage.replace(":", "_") + singularity.suffix
                image = "/".join([hub, image]) if hub != "" else image
                singularity.pull(
                    image, simage, directory=pull_folder, force=args.force)
            else:
                if args.podman:
                    podman.pull("/".join([hub, image]) if hub != "" else image, force=args.force)
                else:
                    docker.pull("/".join([hub, image]) if hub != "" else image, force=args.force)
    else: # no cab bases or images specifically being pulled
        base = []
        repository_ = []
        for cab_ in CAB:
            filename = "/".join([stimela.CAB_PATH, cab_, "parameters.json"])
            param = utils.readJson(filename)

            cabdir = "{:s}/{:s}".format(stimela.CAB_PATH, cab_)
            _cab = info(cabdir, display=False)
            tags = _cab.tag
            if not isinstance(tags, list):
                tags = [tags]
            for tag in tags:
                base.append(f"{_cab.base}:{tag}")
                repository_.append(param["hub"] if "hub" in param.keys() else args.repository)

        assert len(base) == len(repository_)
        uniq_pulls = []
        for hub, image in zip(repository_, base):
            if hub == "docker" or hub == "docker.io":
                hub = ""
            if args.singularity:
                simage = image.replace("/", "_")
                simage = simage.replace(":", "_") + singularity.suffix
                image = "/".join([hub, image]) if hub != "" else image
                if image not in uniq_pulls:
                    uniq_pulls.append(image)
                    singularity.pull(
                        image, simage, directory=pull_folder, force=args.force)
            else:
                image = "/".join([hub, image]) if hub != "" else image
                if image not in uniq_pulls:
                    uniq_pulls.append(image)
                    if args.podman:
                        podman.pull(image, force=args.force)
                    else:
                        docker.pull(image, force=args.force)


def main(argv):
    for i, arg in enumerate(argv):
        if (arg[0] == '-') and arg[1].isdigit():
            argv[i] = ' ' + arg

    parser = ArgumentParser(description='Stimela: Dockerized Radio Interferometric Scripting Framework. '
                            '|n version {:s} |n install path {:s} |n '
                            'Sphesihle Makhathini <sphemakh@gmail.com>'.format(stimela.__version__,
                                                                               os.path.dirname(__file__)),
                            formatter_class=MultilineFormatter,
                            add_help=False)

    add = parser.add_argument

    add("-h", "--help",  action="store_true",
        help="Print help message and exit")

    add("-v", "--version", action='version',
        version='{:s} version {:s}'.format(parser.prog, stimela.__version__))

    add("command", nargs="*", metavar="command [options]",
        help="Stimela command to execute. For example, 'stimela help run'")

    options = []
    commands = dict(pull=pull, build=build, run=run, cabs=cabs)
#                    images=images, ps=ps,
#                    containers=containers, kill=kill,
#                    clean=clean)

    command = "failure"

    for cmd in commands:
        if cmd in argv:
            command = cmd

            index = argv.index(cmd)
            options = argv[index+1:]
            argv = argv[:index+1]

    args = parser.parse_args(argv)

    # Command is help and no other commands following
    try:
        main_help = (args.command[0] == "help" and len(args.command) == 1)
    except IndexError:
        main_help = True

    if args.help or main_help:
        parser.print_help()

        print("""
Run a command. These can be:

help    : Prints out a help message about other commands
build   : Build a set of stimela images
pull    : pull a stimela base images
run     : Run a stimela script
cabs    : Manage cab images

""")

        raise SystemExit

    # Separate commands into command and arguments
    cmd, argv = args.command[0], args.command[1:]

    # If we've got past the if statement above, and help
    # is the command then assume that help on a command
    # is requested
    if cmd == "help":
        # Request help on the sub-command
        cmd, argv = argv[0], ["-h"]
    else:
        argv = options

    # Get the function to execute for the command
    try:
        _cmd = commands[cmd]
    except KeyError:
        raise KeyError("Command '{:s}' not recognized "
                       "Run : 'stimela help' for help".format(cmd))

    # Invoke the command
    _cmd(argv)
