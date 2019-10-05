import os
import sys
import argparse
import time
from  argparse import ArgumentParser
import textwrap as _textwrap
import tempfile
import signal
import inspect
import pkg_resources
import glob
import cwltool.factory
import yaml
import subprocess

try:
    __version__ = pkg_resources.require("stimela")[0].version
except pkg_resources.DistributionNotFound:
    __version__ = "dev"

pckgdir = os.path.dirname(__file__)

GLOBALS = {}

class MultilineFormatter(argparse.HelpFormatter):
    def _fill_text(self, text, width, indent):
        text = self._whitespace_matcher.sub(' ', text).strip()
        paragraphs = text.split('|n ')
        multiline_text = ''
        for paragraph in paragraphs:
            formatted_paragraph = _textwrap.fill(paragraph, width, initial_indent=indent, subsequent_indent=indent) + '\n\n'
            multiline_text = multiline_text + formatted_paragraph
        return multiline_text

def register_globals():
    frame = inspect.currentframe().f_back
    frame.f_globals.update(GLOBALS)


def get_bases():
    """Get base images from stimela cabs

    """

    fac = cwltool.factory.Factory()
    cabs = glob.glob("{0:s}/cargo/cab/*.cwl".format(pckgdir))
    base = []
    for cab in cabs:
        tool = fac.make(cab)
        reqs = tool.t.original_requirements.get('dockerPull', None)
        hints = tool.t.original_hints[0].get('dockerPull', None)
        if reqs:
            base.append(reqs)
        elif hints:
            base.append(hints)
    return base


def log_base(path, image):
    """ Log docker images pulled/built via stimela

    Parameters
    ----------

    path: str
        Path where images should be logged
    """

    try:
        with open(path) as std:
            images = yaml.load(std)
    except IOError:
        images = dict(images=[])

    images["images"].append(image)

    with open(path, 'w') as stdw:
        yaml.dump(images, stdw, default_flow_style=False)


def pull(argv):
    for i, arg in enumerate(argv):
        if (arg[0] == '-') and arg[1].isdigit(): argv[i] = ' ' + arg 

    parser = ArgumentParser(description='Pull docker stimela base images')

    add = parser.add_argument

    add("-image", action="append", metavar="IMAGE[:TAG]",
            help="Pull base image along with its tag (or version). Can be called multiple times")

    add("-t", "--tag",
            help="Tag")

    args = parser.parse_args(argv) 
    path = "{0:s}/.stimela/stimela_base_image_log.json".format(os.environ["HOME"])

    images = args.image or get_bases()
    for image in images:
        if args.tag:
            image_ = "{0:s}:{:1:s}".format(image,args.tag)
        subprocess.check_call(["docker", "pull", image_])
        log_base(path, image_)


def build(argv):
    for i, arg in enumerate(argv):
        if (arg[0] == '-') and arg[1].isdigit(): argv[i] = ' ' + arg 

    parser = ArgumentParser(description='Build stimela base images')

    add = parser.add_argument

    add("-image", action="append", metavar="IMAGE[:TAG]",
            help="Pull base image along with its tag (or version). Can be called multiple times")

    add("-t", "--tag",
            help="Tag")

    add("-nc", "--no-cache",
            help="Do not use cache when building the image")

    args = parser.parse_args(argv)
    path = "{0:s}/.stimela/stimela_base_image_log.json".format(os.environ["HOME"])

    images = args.image or get_bases()
    for image in images:
        if args.tag:
            image_ = "{0:s}:{:1:s}".format(image,args.tag)
        subprocess.check_call(["docker", "build", 
                    "--no-cache" if args.no_cache else "",
                    "-t",
                    image_])
        log_base(path, image_)


def cabs(argv):
    for i, arg in enumerate(argv):
        if (arg[0] == '-') and arg[1].isdigit(): argv[i] = ' ' + arg 

    parser = ArgumentParser(description='Get information about stimela cabs (tasks)')

    add = parser.add_argument

    add("-i", "--info",
            help="Get detailed cab documentation")

    add("-l", "--list",
            help="List stimela cabs")

    add("-ls", "--list-summary",
            help="List stimela cabs with a summary of cab documentation")

    args = parser.parse_args(argv)

    if args.list:
        cabfiles = os.listdir("{0:s}/cargo/cab".format(pckgdir))
        print(( ", ".join( [ a[:-4] for a in cabfiles] )))
    elif args.list_summary:
        cabfiles = glob.glob("{0:s}/cargo/cab".format(pckgdir))
    elif args.info:
        cabfile = "{0:s}/cargo/cab/{1:s}.cwl".format(pckgdir, args.info)
        subprocess.check_call(["cwltool", cabfile, "--help"])

    return 0


def clean(argv):
    for i, arg in enumerate(argv):
        if (arg[0] == '-') and arg[1].isdigit(): argv[i] = ' ' + arg 

    parser = ArgumentParser(description='Delete docker images pulled/built by stimela')
    parser.add_argument("-f", "--force", action="store_true",
        help="Force removal of the image")

    path = "{0:s}/.stimela/stimela_base_image_log.json".format(os.environ["HOME"])
    try:
        with open(path) as stdr:
            images = yaml.load(stdr)
    except IOError:
        print("No images have been logged")
        return

    for image in images.get("images", []):
        subprocess.check_call(["docker", "rmi",
                    "--force" if args.force else "", image])
    return 0


def run(argv):
    for i, arg in enumerate(argv):
        if (arg[0] == '-') and arg[1].isdigit(): argv[i] = ' ' + arg

    parser = ArgumentParser(description='Dockerized Radio Interferometric Scripting Framework.\n'
                                        'Sphesihle Makhathini <sphemakh@gmail.com>')

    add = parser.add_argument

    add("-in", "--input",
            help="Input folder")

    add("-out", "--output",
            help="Output folder")

    add("-ms", "--msdir",
            help="MS folder. MSs should be placed here. Also, empty MSs will be placed here")

    add("script",
            help="Run script")

    add("-g", "--globals", metavar="KEY=VALUE[:TYPE]", action="append", default=[],
            help="Global variables to pass to script. The type is assumed to string unless specified")

    args = parser.parse_args(argv)
    tag =  None

    _globals = dict(_STIMELA_INPUT=args.input, _STIMELA_OUTPUT=args.output,
                    _STIMELA_MSDIR=args.msdir)

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

    with open(args.script, "r") as stdr:
        exec(stdr.read(), _globals)


def main(argv):
    for i, arg in enumerate(argv):
        if (arg[0] == '-') and arg[1].isdigit(): 
            argv[i] = ' ' + arg

    parser = ArgumentParser(description='Stimela: Dockerized Radio Interferometric Scripting Framework. '
                            '|n version {:s} |n install path {:s} |n '
                            'Sphesihle Makhathini <sphemakh@gmail.com>'.format(__version__, pckgdir),
                            formatter_class=MultilineFormatter,
                            add_help=False)

    add = parser.add_argument

    add("-h", "--help",  action="store_true",
            help="Print help message and exit")

    add("-v","--version", action='version',
            version='{:s} version {:s}'.format(parser.prog, __version__))

    add("command", nargs="*", metavar="command [options]",
            help="Stimela command to execute. For example, 'stimela help run'")

    options = []
    commands = dict(pull=pull, build=build, run=run,
                    cabs=cabs, clean=clean)

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

        print ("""
Run a command. These can be:

help    : Prints out a help message about other commands
build   : Build stimela images
pull    : pull stimela images
run     : Run a stimela script
cabs    : Get information about stimela cabs
clean   : Remove stimela docker images
""")

        sys.exit(0)

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
