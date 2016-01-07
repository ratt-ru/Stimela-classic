import os
import sys
import argparse
import time
from  argparse import ArgumentParser
import textwrap as _textwrap

import stimela
from stimela import utils, cargo
from pipeliner import Pipeline

LOG_HOME = os.environ["HOME"] + "/.stimela"
LOG_IMAGES = LOG_HOME + "/stimela_images.log"
LOG_CONTAINERS = LOG_HOME + "/stimela_containers.log"

BASE = os.listdir(cargo.BASE_PATH)
CAB = os.listdir(cargo.CAB_PATH)

__version__ = "0.0.6"


class MultilineFormatter(argparse.HelpFormatter):
    def _fill_text(self, text, width, indent):
        text = self._whitespace_matcher.sub(' ', text).strip()
        paragraphs = text.split('|n ')
        multiline_text = ''
        for paragraph in paragraphs:
            formatted_paragraph = _textwrap.fill(paragraph, width, initial_indent=indent, subsequent_indent=indent) + '\n\n'
            multiline_text = multiline_text + formatted_paragraph
        return multiline_text


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
                       "{:s}/{:s}".format(cargo.BASE_PATH, image)])

    else:
        for image in CAB:
            dockerfile = "{:s}/{:s}".format(cargo.CAB_PATH, image)

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
                    STIMELA_DATA=cargo.DATA_PATH, STIMELA_MSDIR=args.msdir,
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
            _image = image.split(":")

            if len(_image)>1:
                image = _image[0]
                tag = _image[1]
            else:
                tag = "latest"
            
            date = "{:d}/{:d}/{:d} {:d}:{:d}:{:d}".format(*time.localtime()[:6])

            home = os.environ["HOME"] + "/.stimela/stimela_images.log"
            with open(home, "r") as std:
                lines = std.readlines()

            with open(home, "w") as std:
                newline = ["{:s} {:s} {:s}\n".format(image, tag, date)]
                std.write( "".join( lines + newline) )

    else:
        for image in BASE:
            if args.tag:
                image = "{:s}:{:s}".format(image, args.tag)
            utils.xrun("docker pull", ["penthesilea/{:s}".format(image)])

            date = "{:d}/{:d}/{:d}-{:d}:{:d}:{:d}".format(*time.localtime()[:6])

            home = os.environ["HOME"] + "/.stimela/stimela_images.log"

            with open(home, "r") as std:
                lines = std.readlines()

            with open(home, "w") as std:
                newline = ["{:s} {:s} {:s}\n".format(image, args.tag or "latest", date)]
                std.write( "".join( lines + newline) )


def images():
    for i, arg in enumerate(sys.argv):
        if (arg[0] == '-') and arg[1].isdigit(): sys.argv[i] = ' ' + arg
    
    parser = ArgumentParser(description='List all stimela related images.')

    add = parser.add_argument

    add("-c", "--clear", action="store_true",
            help="Clear images log file")

    args = parser.parse_args()

    if args.clear:
        with open(stimela.LOG_IMAGES, "w") as std:
           return


    with open(stimela.LOG_IMAGES, "r") as std:
        lines = std.readlines()

    print("{:<48} {:<32} {:<12}".format("IMAGE", "TAG", "TIME STAMP") )
    for line in lines:
        image, tag, date = line.split()
        print("{:<48} {:<32} {:<12}".format(image, tag, date) )


def ps():
    for i, arg in enumerate(sys.argv):
        if (arg[0] == '-') and arg[1].isdigit(): sys.argv[i] = ' ' + arg
    
    parser = ArgumentParser(description='List all active stimela containers.')

    add = parser.add_argument

    add("-c", "--clear", action="store_true",
            help="Clear containers log file")

    args = parser.parse_args()

    if args.clear:
        with open(stimela.LOG_CONTAINERS, "w") as std:
           return

    with open(stimela.LOG_CONTAINERS, "r") as std:
        lines = std.readlines()

    print("{:<48} {:<24} {:<24} {:>12}".format("CONTAINER", "ID", "UP TIME", "STATUS") )

    for line in lines:
        cont, status, _id, uptime = line.split()
        print("{:<48} {:<24} {:<24} {:>12}".format(cont, status, _id, uptime) )


def main():
    for i, arg in enumerate(sys.argv):
        if (arg[0] == '-') and arg[1].isdigit(): sys.argv[i] = ' ' + arg


    parser = ArgumentParser(description='Stimela: Dockerized Radio Interferometric Scripting Framework. ' 
                                        '|n version {:s} |n Sphesihle Makhathini <sphemakh@gmail.com> |n '.format(__version__),
                            formatter_class=MultilineFormatter, add_help=False)

    add = parser.add_argument

    add("-h", "--help",  action="store_true",
            help="Print help message and exit")

    add("-v","--version", action='version',
            version='{:s} version {:s}'.format(parser.prog, __version__))

    add("command", nargs="*", metavar="command [options]",
            help="Stimela command to execute. For example, 'stimela help run'")

    options = []
    commands = dict(pull=pull, build=build, run=run, images=images, ps=ps)
    command = "help"

    for cmd in commands:
       if cmd in sys.argv:
           command = cmd

           index = sys.argv.index(cmd)
           options = sys.argv[index:]
           sys.argv = sys.argv[: index + 1]

    args = parser.parse_args()

    main_help = lambda : args.command and (args.command[0]=="help") and (len(sys.argv)==2)

    if args.help or len(sys.argv)==1 or main_help():
        parser.print_help()

        print ("""
Run a command. These can be:

help    : Prints out a help message about other commands
build   : Build a set of stimela images
pull    : pull a stimela base images
run     : Run a stimela script
images  : List stimela images
ps      : List initiated containers
""")

        sys.exit(0)

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
