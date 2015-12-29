import os
import sys
import stimela
from stimela import utils
from  argparse import ArgumentParser

__version__ = "0.0.6"

ekhaya = os.path.dirname(__file__)
STABLE_TAG = "stable.11.15"

# Path to base images
STIMELA_BASE_PATH = "{:s}/base".format(ekhaya)

# Path to executor images
STIMELA_CAB_PATH = "{:s}/cab".format(ekhaya)

# Path to native data products
STIMELA_DATA = "{:s}/data".format(ekhaya)

# Path to config templates
STIMELA_CONFIG_TEMPLATES = "{:s}/configs".format(ekhaya)

BASE = os.listdir(STIMELA_BASE_PATH)
CAB = os.listdir(STIMELA_CAB_PATH)


def build():
    for i, arg in enumerate(sys.argv):
        if (arg[0] == '-') and arg[1].isdigit(): sys.argv[i] = ' ' + arg

    parser = ArgumentParser(description='Build dcoker images. Call without arguments \n'
                                        'to build default executor (a.k.a cab) images')

    add = parser.add_argument

    add("-cab", action="store_true",
            help="Build cab images")
    
    add("-base", action="store_true",
            help="Build Base images")

    args = parser.parse_args()

    if args.base:
        for image in BASE:
            utils.xrun("docker build", ["-t", "stimela/{:s}".format(image),
                       "{:s}/{:s}".format(STIMELA_BASE_PATH, image)])

    else:
        for image in CAB:
            dockerfile = "{:s}/{:s}".format(STIMELA_CAB_PATH, image)

            utils.xrun("docker build", ["-t", "cab/{:s}".format(image),
                       dockerfile])


def run():
    for i, arg in enumerate(sys.argv):
        if (arg[0] == '-') and arg[1].isdigit(): sys.argv[i] = ' ' + arg

    parser = ArgumentParser(description='Dockerized Radio Interferometric Scripting Framework.\n' 
                                        'Sphesihle Makhathini <sphemakh@gmail.com>')

    add = parser.add_argument

    add("-in", "--input",
            help="Input folder")

    add("-out", "--output", default="output",
            help="Output folder")

    add("-ms", "--msdir",
            help="MS folder. MSs should be placed here. Also, empty MSs will be placed here")

    add("-L", "--load-from-log", dest="from_log",  metavar="LOG:TAG[:DIR]",
            help="Load base images from stimela log file. The resulting executor images will be tagged 'TAG', and the build contexts will be stored at 'DIR'")

    add("script",
            help="Penthesilea script")

    args = parser.parse_args()

    tag =  None

    if args.from_log:
        
        destdir = "."

        tmp = args.from_log.split(":")
        if len(tmp) == 2:
            log, tag = tmp
        elif len(tmp) == 3:
            log, tag, destdir = tmp
            if not os.path.exists(destdir):
                os.mkdir(destdir)

        images = set(utils.get_base_images(log))

        for image in images:

            image_, base = image
            path = "{:s}/{:s}".format(STIMELA_CAB_PATH, image_.split("/")[-1])
            dirname, dockerfile = utils.change_Dockerfile_base_image(path, base, image_.split("/")[-1], destdir=destdir)

            # Build executor image
            utils.xrun("docker build", ["-t", 
                       "cab/{:s}:{:s}".format(image_.split("/")[-1], tag), 
                       "-f", dockerfile, dirname])

    _globals = dict(STIMELA_INPUT=args.input, STIMELA_OUTPUT=args.output, 
                    STIMELA_DATA=STIMELA_DATA, STIMELA_MSDIR=args.msdir,
                    CAB_TAG=tag)


    execfile(args.script, _globals)


def pull():
    for i, arg in enumerate(sys.argv):
        if (arg[0] == '-') and arg[1].isdigit(): sys.argv[i] = ' ' + arg
    
    parser = ArgumentParser(description='Pull docker stimela base images')

    add = parser.add_argument

    add("-image", action="append", metavar="IMAGE[:TAG]",
            help="Pull base image along with its tag (or version). Can be called multiple times")

    add("-t", "--tag",
            help="Tag")

    args = parser.parse_args()

    if args.image:
        for image in args.image:
            # still using penthesilea on docker hub
            utils.xrun("docker pull", [image])
    else:
        for image in BASE:
            if args.tag:
                image = "{:s}:{:s}".format(image, args.tag)
            utils.xrun("docker pull", ["penthesilea/{:s}".format(image)])


def main():
    for i, arg in enumerate(sys.argv):
        if (arg[0] == '-') and arg[1].isdigit(): sys.argv[i] = ' ' + arg

    message = "Run a command. These can be:\n \n \
help    : Prints out a help message about other commands\n \n \
build   : Build a set of stimela images\n \n \
pull    : pull a stimela base images\n \n \
run     : Run a stimela script\n"

    parser = ArgumentParser(description='Dockerized Radio Interferometric Scripting Framework.\n' 
                                        'Sphesihle Makhathini <sphemakh@gmail.com>\n \n \n{:s}'.format(message))

    add = parser.add_argument

    add("-v","--version", action='version',
            version='{:s} version {:s}'.format(parser.prog, __version__))

    add("command", nargs="*", metavar="command [options]",
            help=message)

    options = []
    commands = dict(pull=pull, build=build, run=run)
    command = "help"

    for cmd in commands:
       if cmd in sys.argv:
           command = cmd

           index = sys.argv.index(cmd)
           options = sys.argv[index:]
           sys.argv = sys.argv[: index + 1]

    # Print help info if called without options
    if len(sys.argv) == 1:
        sys.argv += ["-h"]

    args = parser.parse_args()

    if args.command:
        if args.command[0] == "help":
            sys.argv = sys.argv[1:] + ["-h"]
        else:
            sys.argv = options
        try:
            _cmd = commands[command]
        except ValueError:
            raise ValueError("Command '{:s}' not recognized\n "
                             "Run : 'stimela help' for help".format(command))
        _cmd()
