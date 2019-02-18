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
from stimela.cargo import cab
from recipe import Recipe as Pipeline
from recipe import Recipe, PipelineException
from stimela import docker, singularity
import pkg_resources

try:
    __version__ = pkg_resources.require("stimela")[0].version
except pkg_resources.DistributionNotFound:
    __version__ = "dev"

from stimela.utils import logger

# Get to know user
USER = os.environ["USER"]
UID = os.getuid()
GID = os.getgid()

# Set up logging infrastructure
LOG_HOME = os.path.expanduser("~/.stimela")
# This is is the default log file. It logs stimela images, containers and processes
LOG_FILE = "{0:s}/stimela_logfile.json".format(LOG_HOME)
#LOG_FILE = "{0:s}/{1:s}_stimela_logfile.json".format(LOG_HOME, USER)


# Get base images
# All base images must be on dockerhub
BASE = os.listdir(cargo.BASE_PATH)

# Get package cab images (user can add their own cab images)
# All package cab images must be based on stimela base images.

CAB = []
for item in os.listdir(cargo.CAB_PATH):
    try: 
        # These files must exist for a cab image to be valid
        ls_cabdir = os.listdir('{0}/{1}'.format(cargo.CAB_PATH, item))
        dockerfile = 'Dockerfile' in ls_cabdir
        paramfile = 'parameters.json' in ls_cabdir
        srcdir = 'src' in ls_cabdir
    except OSError:
        continue
    if dockerfile and paramfile and srcdir:
        CAB.append(item)

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


def build(argv):
    for i, arg in enumerate(argv):
        if (arg[0] == '-') and arg[1].isdigit(): argv = ' ' + arg

    parser = ArgumentParser(description='Build executor (a.k.a cab) images')
    parser.add_argument("-b", "--base", action="store_true",
            help="Build base images")

    parser.add_argument("-c", "--cab", metavar="CAB,CAB_DIR",
            help="Executor image (name) name, location of executor image files")

    parser.add_argument("-uo", "--us-only",
            help="Only build these cabs. Comma separated cab names")

    parser.add_argument("-i", "--ignore-cabs", default="",
            help="Comma separated cabs (executor images) to ignore.")

    parser.add_argument("-nc", "--no-cache", action="store_true",
            help="Do not use cache when building the image")

    parser.add_argument("-bl", "--build-label", default=USER,
            help="Label for cab images. All cab images will be named <CAB_LABEL>_<cab name>. The default is $USER")

    args = parser.parse_args(argv)
    log = logger.StimelaLogger('{0:s}/{1:s}_stimela_logfile.json'.format(LOG_HOME, args.build_label))

    if args.base:
        # Build base and meqtrees images first
        BASE.remove("base")
        BASE.remove("meqtrees")
        BASE.remove("casa")
        
        for image in ["base", "meqtrees", "casa"] + BASE:
            dockerfile = "{:s}/{:s}".format(cargo.BASE_PATH, image)
            image = "stimela/{0}:{1}".format(image, __version__)
            docker.build(image,
                         dockerfile)

        log.log_image(image, dockerfile, replace=True)
        log.write()

        return 0

    workdir = "/home/{}/output/".format(USER)
    build_args = [
                  "WORKDIR {:s}".format(workdir),
                  "RUN useradd -r -u {0:d} -U {1:s}".format(UID, USER),
                  "USER {0:s}".format(USER),
                  ]

    no_cache = ["--no-cache"] if args.no_cache else []


    if args.cab:
        cab_args = args.cab.split(",")

        if len(cab_args)==2:
            cab, path = cab_args
        else:
            raise ValueError("Not enough arguments for build command.")

        image = "{:s}_cab/{:s}".format(args.build_label, cab)

        docker.build(image,
                     path,
                     build_args=build_args, args=no_cache)

        log.log_image(image, path, replace=True, cab=True)
        log.write()
        return

    # Cabs and their locations   
    cabs = []
    dockerfiles = []

    if args.us_only:
        CABS = args.us_only.split(',')
    else:
        # Images that have been logged
        # This is crucial for making custom cabs
        logged_images = log.read().get('images', {})
        for key,val in logged_images.iteritems():
            if val['CAB']:
                cabs.append(key)
                dockerfiles.append(val['DIR'])
        # If user wants to ignore some cabs
        IGNORE = args.ignore_cabs.split(",")
        CABS = set(CAB).difference(set(IGNORE))

    # Prioritise package images over logged images
    cabs = ["{:s}_cab/{:s}".format(args.build_label, cab) for cab in CABS] + cabs
    dockerfiles = [ "{:s}/{:s}".format(cargo.CAB_PATH, cab) for cab in CABS] + dockerfiles
    built = []
    for image, dockerfile in zip(cabs,dockerfiles):
        if image not in built:
            docker.build(image,
                         dockerfile,
                         build_args=build_args, args=no_cache)

            log.log_image(image, dockerfile, replace=True, cab=True)
            log.write()
            built.append(image)


def get_cabs(logfile):
    log = logger.StimelaLogger(logfile)
    cabs_ = log.read()['images']
    
    # Remove images that are not cabs
    for key in cabs_.keys():
        if not cabs_[key]['CAB']:
            del cabs_[key]

    return cabs_


def info(cabdir, header=False):
    """ prints out help information about a cab """

    # First check if cab exists
    pfile = "{}/parameters.json".format(cabdir)
    if not os.path.exists(pfile):
        raise RuntimeError("Cab could not be found at : {}".format(cabdir))
    # Get cab info
    cab_definition = cab.CabDefinition(parameter_file=pfile)
    cab_definition.display(header)


def cabs(argv):
    for i, arg in enumerate(argv):
        if (arg[0] == '-') and arg[1].isdigit(): argv = ' ' + arg

    parser = ArgumentParser(description='List executor (a.k.a cab) images')
    parser.add_argument("-i", "--cab-doc", 
        help="Will display document about the specified cab. For example, \
to get help on the 'cleanmask cab' run 'stimela cabs --cab-doc cleanmask'")

    parser.add_argument("-l", "--list", action="store_true",
            help="List cab names")

    parser.add_argument("-ls", "--list-summary", action="store_true",
            help="List cabs with a summary of the cab")

    parser.add_argument("-bl", "--build-label", default=USER,
            help="Label for build you want documentation for. See --build-label option in 'stimela help build'")

    args = parser.parse_args(argv)
    logfile = '{0:s}/{1:s}_stimela_logfile.json'.format(LOG_HOME, args.build_label)

    cabs_ = get_cabs(logfile)
    if cabs_:
        pass
    else:
        print('No cab images found, did you run \'stimela build\'')
        sys.exit(0)

    if args.cab_doc:
        name = '{0:s}_cab/{1:s}'.format(args.build_label, args.cab_doc)
        try:
            cabdir = cabs_[name]['DIR']
        except KeyError:
            raise RuntimeError('The cab you requested is not known to stimela, or has not been built. Run \'stimela cabs -l\' to see which cabs have been built')
        info(cabdir)

    elif args.list_summary:
        for key,val in cabs_.iteritems():
            if not val['CAB']:
                continue
            cabdir = cabs_[key]['DIR']
            try:
                info(cabdir, header=True)
            except IOError:
                pass
    else:
        _cabs = []
        for cab in cabs_:
            # strip away the label
            name = cab.split('{}_'.format(args.build_label))[1].split('/')[1]
            _cabs.append(name)
        # print them cabs
        print( ', '.join(_cabs) )


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

    add("-j", "--ncores", type=int,
            help="Number of cores to when stimela parallesization (stimea.utils.pper function) ")

    add("script",
            help="Run script")

    add("-g", "--globals", metavar="KEY=VALUE[:TYPE]", action="append", default=[],
            help="Global variables to pass to script. The type is assumed to string unless specified")

    add("-bl", "--build-label", default=USER,
            help="Label for cab images. All cab images will be named <CAB_LABEL>_<cab name>. The default is $USER")

    args = parser.parse_args(argv)
    tag =  None

    _globals = dict(_STIMELA_INPUT=args.input, _STIMELA_OUTPUT=args.output,
                    _STIMELA_MSDIR=args.msdir,
                    CAB_TAG=tag, _STIMELA_BUILD_LABEL=args.build_label)

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


def pull(argv):
    for i, arg in enumerate(argv):
        if (arg[0] == '-') and arg[1].isdigit(): argv[i] = ' ' + arg

    parser = ArgumentParser(description='Pull docker stimela base images')

    add = parser.add_argument

    add("-im", "--image", action="append", metavar="IMAGE[:TAG]",
            help="Pull base image along with its tag (or version). Can be called multiple times")

    add("-t", "--tag",
            help="Tag")

    add("-s", "--singularity", action="store_true",
            help="Use singularity instead of docker."
                 "Images will be pulled into the directory specified by the enviroment varaible, SINGULARITY_PULLFOLDER. $PWD by default")

    args = parser.parse_args(argv)
    log = logger.StimelaLogger(LOG_FILE)
    images = log.read()['images']

    if args.image:
        for image in args.image:

            simage = image.replace("/", "_")
            simage = simage.replace(":", "_") + ".img"
            if args.singularity:
                singularity.pull(image, simage)
            else:
                docker.pull(image)
                log.log_image(image, 'pulled')
    else:

        base = []
        for cab in CAB:
            image = "{:s}/{:s}".format(cargo.CAB_PATH, cab)
            base.append( utils.get_Dockerfile_base_image(image).split()[-1] )

        base = set(base)

        for image in base:
            if image not in ["stimela/ddfacet", "radioastro/ddfacet"]:
                if args.singularity:
                    simage = image.replace("/", "_")
                    simage = simage.replace(":", "_") + ".img"
                    singularity.pull(image, simage)
                else:
                    docker.pull(image)
                    log.log_image(image, 'pulled')

    log.write()


def images(argv):
    for i, arg in enumerate(argv):
        if (arg[0] == '-') and arg[1].isdigit(): argv[i] = ' ' + arg

    parser = ArgumentParser(description='List all stimela related images.')

    add = parser.add_argument

    add("-c", "--clear", action="store_true",
            help="Clear the logfile that keeps track of stimela images. This does not do anythig to the images.")

    args = parser.parse_args(argv)

    log = logger.StimelaLogger(LOG_FILE)
    log.display('images')

    if args.clear:
        log.clear('images')
        log.write()


def containers(argv):
    for i, arg in enumerate(argv):
        if (arg[0] == '-') and arg[1].isdigit(): argv[i] = ' ' + arg

    parser = ArgumentParser(description='List all active stimela containers.')

    add = parser.add_argument

    add("-c", "--clear", action="store_true",
            help="Clear the log file that keeps track of stimela containers. This doesn't do anything to the containers.")

    args = parser.parse_args(argv)

    log = logger.StimelaLogger(LOG_FILE)
    log.display('containers')
    if args.clear:
        log.clear('containers')
        log.write()


def ps(argv):
    for i, arg in enumerate(argv):
        if (arg[0] == '-') and arg[1].isdigit(): argv[i] = ' ' + arg

    parser = ArgumentParser(description='List all running stimela processes')

    add = parser.add_argument

    add("-c", "--clear", action="store_true",
            help="Clear logfile that keeps track of stimela processes. This doesn't do anything ot the processes themselves.")

    args = parser.parse_args(argv)

    log = logger.StimelaLogger(LOG_FILE)
    log.display('processes')
    if args.clear:
        log.clear('processes')
        log.write()


def kill(argv):
    for i, arg in enumerate(argv):
        if (arg[0] == '-') and arg[1].isdigit(): argv[i] = ' ' + arg

    parser = ArgumentParser(description='Gracefully kill stimela process(s).')

    add = parser.add_argument

    add("pid", nargs="*",
            help="Process ID")

    args = parser.parse_args(argv)

    log = logger.StimelaLogger(LOG_FILE)

    for pid in args.pid:

        found = pid in log.info['processes'].keys()

        if not found:
            print("Could not find process {0}".format(pid))
            continue

        try:
            os.kill(int(pid), signal.SIGINT)
        except OSError:
            raise OSError('Process with PID {} could not be killed'.format(pid))

        log.remove('processes', pid)
    log.write()


def clean(argv):
    for i, arg in enumerate(argv):
        if (arg[0] == '-') and arg[1].isdigit(): argv[i] = ' ' + arg

    parser = ArgumentParser(description='Convience tools for cleaning up after stimela')
    add = parser.add_argument

    add("-ai", "--all-images", action="store_true",
        help="Remove all images pulled/built by stimela. This include CAB images")
    
    add("-ab", "--all-base", action="store_true",
        help="Remove all base images")

    add("-ac", "--all-cabs", action="store_true", 
        help="Remove all CAB images")

    add("-aC", "--all-containers", action="store_true",
        help="Stop and/or Remove all stimela containers")
    
    add("-bl", "--build-label", default=USER,
            help="Label for cab images. All cab images will be named <CAB_LABEL>_<cab name>. The default is $USER")

    args = parser.parse_args(argv)

    log = logger.StimelaLogger(LOG_FILE)
    log_cabs = logger.StimelaLogger('{0:s}/{1:s}_stimela_logfile.json'.format(LOG_HOME, 
            args.build_label))

    if args.all_images:
        images = log.info['images'].keys()
        images = log_cabs.info['images'].keys()
        for image in images:
            utils.xrun('docker', ['rmi', image])
            log.remove('images', image)
            log.write()
        
        images = log_cabs.info['images'].keys()
        for image in images:
            if log_cabs.info['images'][image]['CAB']:
                utils.xrun('docker', ['rmi', image])
                log_cabs.remove('images', image)
                log_cabs.write()

    if args.all_base:
        images = log.info['images'].keys()
        for image in images:
            if log.info['images'][image]['CAB'] is False:
                utils.xrun('docker', ['rmi', image])
                log.remove('images', image)
                log.write()

    if args.all_cabs:
        images = log_cabs.info['images'].keys()
        for image in images:
            if log_cabs.info['images'][image]['CAB']:
                utils.xrun('docker', ['rmi', image])
                log_cabs.remove('images', image)
                log_cabs.write()
        
    if args.all_containers:
        containers = log.info['containers'].keys()
        for container in containers:
            print container
            cont = docker.Container(log.info['containers'][container]['IMAGE'], container)
            try:
                status = cont.info()['State']['Status'].lower()
            except:
                print('Could not inspect container {}. It probably doesn\'t exist, will remove it from log'.format(container))
                status = "no there"

            if status == 'running':
            # Kill the container instead of stopping it, so that effect can be felt py parent process
                utils.xrun('docker', ['kill', container])
                cont.remove()
            elif status in ['exited', 'dead']:
                cont.remove()

            log.remove('containers', container)
            log.write()

def main(argv):
    for i, arg in enumerate(argv):
        if (arg[0] == '-') and arg[1].isdigit(): argv[i] = ' ' + arg


    parser = ArgumentParser(description='Stimela: Dockerized Radio Interferometric Scripting Framework. '
                            '|n version {:s} |n install path {:s} |n '
                            'Sphesihle Makhathini <sphemakh@gmail.com>'.format(__version__,
                                                                               os.path.dirname(__file__)),
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
                    images=images, cabs=cabs, ps=ps,
                    containers=containers, kill=kill,
                    clean=clean)

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
build   : Build a set of stimela images
pull    : pull a stimela base images
run     : Run a stimela script
images  : List stimela images
cabs    : Manage cab images
ps      : List running stimela scripts
kill    : Gracefully kill runing stimela process
clean   : Clean up tools for stimela

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
