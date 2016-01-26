import os
import sys
import argparse
import time
from  argparse import ArgumentParser
import textwrap as _textwrap
import tempfile
import signal

import inspect
import stimela
from stimela import utils, cargo
from recipe import Recipe as Pipeline
from recipe import Recipe
import stimela.stimela_docker as docker

LOG_HOME = os.path.expanduser("~/.stimela")
LOG_IMAGES = LOG_HOME + "/stimela_images.log"
LOG_CONTAINERS = LOG_HOME + "/stimela_containers.log"
LOG_PROCESS = LOG_HOME + "/stimela_process.log"

BASE = os.listdir(cargo.BASE_PATH)
CAB = os.listdir(cargo.CAB_PATH)

__version__ = "0.1.0"
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

    new = ["base", "casa", "meqtrees", "lwimager"]
    for image in BASE:
        if image not in new:
            new.append(image)

    if args.base:
        for image in new:
            docker.build("stimela/{:s}".format(image),
                         "{:s}/{:s}".format(cargo.BASE_PATH, image))

    else:
        for image in CAB:
            dockerfile = "{:s}/{:s}".format(cargo.CAB_PATH, image)

            docker.build("cab/{:s}".format(image),
                       dockerfile)


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

    add("-j", "--ncores", type=int,
            help="Number of cores to when stimela parallesization (stimea.utils.pper function) ")

    add("-L", "--load-from-log", dest="from_log",  metavar="LOG:TAG[:DIR]",
            help="Load base images from stimela log file. The resulting executor images will be tagged 'TAG', and the build contexts will be stored at 'DIR'")

    add("script",
            help="Penthesilea script")

    add("-g", "--globals", metavar="KEY=VALUE[:TYPE]", action="append", default=[],
            help="Global variables to pass to script. The type is assumed to string unless specified")

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
            docker.build("cab/{:s}:{:s}".format(image_.split("/")[-1], tag), 
                       dirname)

    _globals = dict(STIMELA_INPUT=args.input, STIMELA_OUTPUT=args.output, 
                    STIMELA_DATA=cargo.DATA_PATH, STIMELA_MSDIR=args.msdir,
                    CAB_TAG=tag)

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

    if args.ncores:
        utils.CPUS = args.ncores

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

    add("-f", "--force", action="store_true",
            help="Pull image even if it already exists")

    args = parser.parse_args()

    if args.image:
        for image in args.image:
            # still using penthesilea on docker hub
            docker.pull(image)
            _image = image.split(":")

            if len(_image)>1:
                image = _image[0]
                tag = _image[1]
            else:
                tag = "latest"
            
            date = "{:d}/{:d}/{:d} {:d}:{:d}:{:d}".format(*time.localtime()[:6])

            with open(LOG_IMAGES, "r") as std:
                lines = std.readlines()

            with open(home, "w") as std:
                newline = ["{:s} {:s} {:s}\n".format(image, tag, date)]
                std.write( "".join( lines + newline) )

    else:
        for image in BASE:
            tagged = len(image.split(":"))==2

            if not tagged and args.tag:
                image = "{:s}:{:s}".format(image, args.tag)
            elif not tagged:
                image += ":latest"

            with open(LOG_IMAGES, "r") as std:
                lines = std.readlines()
            
            exists = False
            cline = None
            for line in lines:
                new = image.split(":")
                old = line.split()[:2]
                old[0] = old[0].split(":")[0]

                if new == old:
                    if not args.force:
                        print("Image [{:s}] already exists. Add --force/-f to pull it either way".format(image))
                    exists = True
                    cline = line
                    break

            if not exists or args.force:        
                docker.pull("stimela/{:s}".format(image))
                if exists:
                    lines.remove(cline)

            date = "{:d}/{:d}/{:d}-{:d}:{:d}:{:d}".format(*time.localtime()[:6])

            with open(LOG_IMAGES, "w") as std:
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


def cabs():
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

    print("{:<48} {:<24} {:<24} {:<24} {:>12}".format("CONTAINER", "ID", "UP TIME", "PID", "STATUS") )

    for line in lines:
        cont, _id, uptime, pid, status = line.split()
        print("{:<48} {:<24} {:<24} {:<24} {:>12}".format(cont, _id, uptime, pid, status) )


def ps():
    for i, arg in enumerate(sys.argv):
        if (arg[0] == '-') and arg[1].isdigit(): sys.argv[i] = ' ' + arg
    
    parser = ArgumentParser(description='List all running stimela processes')

    add = parser.add_argument
    
    add("-c", "--clear", action="store_true",
            help="Clear Log file")

    args = parser.parse_args()

    with open(stimela.LOG_PROCESS, "r") as std:
        lines = std.readlines()

    print("{:<48} {:<24} {:>12}".format("NAME", "DATE", "PID") )

    for line in lines:
        name, date, pid = line.split()
        print("{:<48} {:<24} {:>12}".format(name, date, pid) )

    if args.clear:
        with open(stimela.LOG_PROCESS, "w") as std:
            pass
    


def kill():
    for i, arg in enumerate(sys.argv):
        if (arg[0] == '-') and arg[1].isdigit(): sys.argv[i] = ' ' + arg
    
    parser = ArgumentParser(description='List all active stimela containers.')

    add = parser.add_argument

    add("pid", nargs="*",
            help="Process ID")

    args = parser.parse_args()


    with open(stimela.LOG_PROCESS) as std:
        procs = std.readlines()

    def found_pid(pid):
        for proc in procs:
            _pid = proc.split()[-1]
            if int(_pid) == int(pid):
                return True, proc
        return False, None

    with open(stimela.LOG_CONTAINERS, "r") as std:
        lines = std.readlines()

    for pid in args.pid:
        pip = int(pid)

        found, proc = found_pid(pid)
        if not found:
            print "Could not find process {0}".format(pid)
            continue

        sucess = False
        for line in lines:
            cont, _id, utime, _pid, status, = line.split()
            if int(pid) == int(_pid):
                if status.find("removed")<0:
                    cont_ = docker.Load(None, cont)
                    cont_.started = True
                    cont_.stop()
                    cont_.rm()
        procs.remove(proc)

        os.kill(int(pid), signal.SIGKILL)


        with open(stimela.LOG_PROCESS, "w") as std:
            std.write("".join(procs))
                

def main():
    for i, arg in enumerate(sys.argv):
        if (arg[0] == '-') and arg[1].isdigit(): sys.argv[i] = ' ' + arg


    parser = ArgumentParser(description='Stimela: Dockerized Radio Interferometric Scripting Framework. ' 
                                        '|n version {:s} |n Sphesihle Makhathini <sphemakh@gmail.com>'.format(__version__),
                            formatter_class=MultilineFormatter, add_help=False)

    add = parser.add_argument

    add("-h", "--help",  action="store_true",
            help="Print help message and exit")

    add("-v","--version", action='version',
            version='{:s} version {:s}'.format(parser.prog, __version__))

    add("command", nargs="*", metavar="command [options]",
            help="Stimela command to execute. For example, 'stimela help run'")

    options = []
    commands = dict(pull=pull, build=build, run=run, 
                    images=images, cabs=cabs, ps=ps,
                    kill=kill)

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
cabs    : List active stimela containers
ps      : List running stimela scripts
kill    : Gracefully kill runing stimela process

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
