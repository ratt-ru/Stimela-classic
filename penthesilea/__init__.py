import os
import sys
import otrera
from otrera import utils
from  argparse import ArgumentParser

__version__ = "0.0.6"

ekhaya = os.path.dirname(__file__)
STABLE_TAG = "stable.11.15"

# Path to base images
PENTHESILEA_BASE_PATH = "{:s}/base".format(ekhaya)

# Path to executor images
PENTHESILEA_ARES_PATH = "{:s}/ares".format(ekhaya)

# Path to native data products
PENTHESILEA_DATA = "{:s}/data".format(ekhaya)

# Path to config templates
PENTHESILEA_CONFIG_TEMPLATES = "{:s}/configs".format(ekhaya)

BASE = os.listdir(PENTHESILEA_BASE_PATH)
ARES = os.listdir(PENTHESILEA_ARES_PATH)


def build():
    for i, arg in enumerate(sys.argv):
        if (arg[0] == '-') and arg[1].isdigit(): sys.argv[i] = ' ' + arg

    parser = ArgumentParser(description='Build dcoker images. Call without arguments \n'
                                        'to build default executor (a.k.a ares) images')

    add = parser.add_argument

    add("-ares", action="store_true",
            help="Build Ares images")
    
    add("-base", action="store_true",
            help="Build Base images")

    args = parser.parse_args()

    if args.base:
        for image in BASE:
            utils.xrun("docker build", ["-t", "penthesilea/{:s}".format(image),
                       "{:s}/{:s}".format(PENTHESILEA_BASE_PATH, image)])

    else:
        for image in ARES:
            dockerfile = "{:s}/{:s}".format(PENTHESILEA_ARES_PATH, image)

            utils.xrun("docker build", ["-t", "ares/{:s}".format(image),
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
            help="Load base images from penthesilea log file. The resulting executor images will be tagged 'TAG', and the build contexts will be stored at 'DIR'")

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
            path = "{:s}/{:s}".format(PENTHESILEA_ARES_PATH, image_.split("/")[-1])
            dirname, dockerfile = utils.change_Dockerfile_base_image(path, base, image_.split("/")[-1], destdir=destdir)

            # Build executor image
            utils.xrun("docker build", ["-t", 
                       "{:s}:{:s}".format(image_, tag), 
                       "-f", dockerfile, dirname])

    _globals = dict(INPUT=args.input, OUTPUT=args.output, 
                    DATA=PENTHESILEA_DATA, MSDIR=args.msdir,
                    ARES_TAG=tag)


    execfile(args.script, _globals)


def pull():
    for i, arg in enumerate(sys.argv):
        if (arg[0] == '-') and arg[1].isdigit(): sys.argv[i] = ' ' + arg
    
    parser = ArgumentParser(description='Pull docker penthesilea base images')

    add = parser.add_argument

    add("-image", action="append", metavar="IMAGE[:TAG]",
            help="Pull base image along with its tag (or version). Can be called multiple times")

    args = parser.parse_args()

    if args.image:
        for image in args.image:
            utils.xrun("docker pull", ["penthesilea/{:s}".format(image)])


def main():
    for i, arg in enumerate(sys.argv):
        if (arg[0] == '-') and arg[1].isdigit(): sys.argv[i] = ' ' + arg

    message = "Run a command. These can be:\n \n \
help    : Prints out a help message about other commands\n \n \
build   : Build a set of penthesilea images\n \n \
pull    : pull a penthesilea base images\n \n \
run     : Run a penthesilea script\n"

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
                             "Run : 'penthesilea help' for help".format(command))
        _cmd()
