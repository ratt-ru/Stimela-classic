# -*- coding: future_fstrings -*-
import subprocess
import os
import platform
import getpass
from io import StringIO
from stimela import utils
import json
import stimela
import time
import datetime
import subprocess
import yaml
from typing import Any, List, Dict, Optional, Union
from stimela.config import StimelaImage

class DockerError(Exception):
    pass

from stimela.backends import StimelaImageBuildInfo, StimelaImageInfo

_available_images: Union[Dict[str,Dict[str, StimelaImageInfo]], None] = None

def available_images():
    """Scans system for available stimela images and returns dicitonary of StimelaImageInfo objects.

    Stimela docker images are identified by a stimela.image.name label.

    Returns
    -------
    dict
        dictionary: {image_name: {version: image_info}}  
    """
    from stimela.main import log
    global _available_images
    if _available_images is None:

        # get list of image IDs which have the right label
        proc = subprocess.run(["docker", "images",
                            "--filter", "label=stimela.image.name", 
                            "--format", "{{.ID}}"], stdout=subprocess.PIPE)
        _available_images = {}
        iids = proc.stdout.split()

        # inspect details of matching IDs
        if iids:
            proc = subprocess.run(["docker", "inspect"] + iids, 
                                stdout=subprocess.PIPE)
            # parse output
            inspect_data = yaml.safe_load(proc.stdout)
            for num, image_data in enumerate(inspect_data):
                iid = image_data.get('Id')
                repotags = image_data.get('RepoTags')
                if iid is None:
                    log.warning(f"failed to parse 'docker inspect' output element {num} {repotags}, skipping")
                    continue
                try:
                    labels = image_data['ContainerConfig']['Labels']
                    name = labels['stimela.image.name']
                    version = labels['stimela.image.version']
                    build = {}
                    for key in 'stimela_version', 'user', 'host', 'date':
                        build[key] = labels[f'stimela.build.{key}']
                except KeyError as keyerr:
                    log.warning(f"failed to parse 'docker inspect' output element {num} {repotags}: missing key {keyerr}, skipping")
                    continue

                _available_images.setdefault(name, {})[version] = StimelaImageInfo(name=name, version=version, iid=iid, 
                                                                                   full_name=repotags[0], build=StimelaImageBuildInfo(**build))
        
    return _available_images


def _get_full_name(image: StimelaImage, version:str):
    """Returns full image name (e.g. "quay.io/stimela/v2-NAME:VERSION")

    Parameters
    ----------
    image : StimelaImage
        image object
    version : str
        version
    """
    from stimela.main import CONFIG
    if CONFIG.opts.registry:
        basename = f"{CONFIG.opts.registry}/{CONFIG.opts.basename}"
    else:
        basename = CONFIG.opts.basename
    return f"{basename}{image.name}:{version}"


def build(image: StimelaImage, version: str):
    """Builds given image + version

    Parameters
    ----------
    image : StimelaImage
        image object
    version : str
        version to be built, must be present in image.images
    """
    from stimela.main import log

    fullname = _get_full_name(image, version)

    build_info = image.images[version]
    cwd = os.path.dirname(image.path)
    dockerfile = os.path.join(cwd, build_info.dockerfile)
    log.info(f"building {fullname} using {dockerfile}")

    subprocess.run(["docker", "build", "-t", fullname, "-f", dockerfile,
                    "--label", f"stimela.image.name={image.name}", 
                    "--label", f"stimela.image.version={version}", 
                    "--label", f"stimela.build.stimela_version={stimela.__version__}", 
                    "--label", f"stimela.build.user={getpass.getuser()}", 
                    "--label", f"stimela.build.host={platform.node()}", 
                    "--label", f"stimela.build.date={datetime.datetime.now().ctime()}", 
                    cwd], check=True)

    # reset this to force a rescan in available_images()
    global _available_images
    _available_images = None


def push(image: StimelaImage, version: str):
    """Pushes given image + version to registry

    Parameters
    ----------
    image : StimelaImage
        image object
    version : str
        version to be pushed
    """
    from stimela.main import log

    fullname = _get_full_name(image, version)
    log.info(f"pushing {fullname}")

    subprocess.run(["docker", "push", fullname], check=True)
        


def pull(image, tag=None, force=False):
    """ pull a docker image """
    if tag:
        image = ":".join([image, tag])

    utils.xrun("docker", ["pull", image])


def seconds_hms(seconds):
    return str(datetime.timedelta(seconds=seconds))


class Container(object):
    def __init__(self, image, name,
                 volumes=None, environs=None,
                 label="", logger=None,
                 time_out=-1,
                 workdir=None,
                 log_container=None,
                 cabname=None,
                 runscript=None):
        """
        Python wrapper to docker engine tools for managing containers.
        """

        self.image = image
        self.name = name
        self.cabnane = cabname
        self.label = label
        self.volumes = volumes or []
        self.environs = environs or []
        self.logger = logger
        self.status = None
        self.WORKDIR = workdir
        self.RUNSCRIPT = runscript
        self.PID = os.getpid()
        self.uptime = "00:00:00"
        self.time_out = time_out
        self.cont_logger = utils.logger.StimelaLogger(
            log_container or stimela.LOG_FILE, jtype="docker")

    def add_volume(self, host, container, perm="rw", noverify=False):

        if os.path.exists(host) or noverify:
            if self.logger:
                self.logger.debug("Mounting volume [{0}] in container [{1}] at [{2}]".format(
                    host, self.name, container))
            host = os.path.abspath(host)
        else:
            raise IOError(
                "Directory {0} cannot be mounted on container: File doesn't exist".format(host))

        self.volumes.append(":".join([host, container, perm]))

    def add_environ(self, key, value):
        if self.logger:
            self.logger.debug("Adding environ varaible [{0}={1}] in container {2}".format(
                key, value, self.name))
        self.environs.append("=".join([key, value]))

    def create(self, *args):

        if self.volumes:
            volumes = " -v " + " -v ".join(self.volumes)
        else:
            volumes = ""
        if self.environs:
            environs = environs = " -e "+" -e ".join(self.environs)
        else:
            environs = ""

        self._print(
            "Instantiating container [{}]. The container ID is printed below.".format(self.name))
        utils.xrun("docker create", list(args) + [volumes, environs, "--rm",
                                                  "-w %s" % (self.WORKDIR),
                                                  "--name", self.name,
                                                  self.image,
                                                  self.RUNSCRIPT or ""], log=self.logger)

        self.status = "created"

    def info(self):

        output = subprocess.check_output(
            "docker inspect {}".format(self.name), shell=True).decode()
        output_file = StringIO(output[3:-3])
        jdict = json.load(output_file)
        output_file.close()

        return jdict

    def get_log(self):
        stdout = open(self.logfile, 'w')
        exit_status = subprocess.call("docker logs {0}".format(self.name),
                                      stdout=stdout, stderr=stdout, shell=True)
        if exit_status != 0:
            self.logger.warn(
                'Could not log container: {}. Something went wrong durring execution'.format(self.name))
            output = 'Task was not started.'
            stdout.write(output)
        else:
            output = stdout.read()

        stdout.close()
        return output

    def start(self, output_wrangler=None):
        running = True
        tstart = time.time()
        self.status = "running"

        self.cont_logger.log_container(self.name)
        self.cont_logger.write()
        self._print("Starting container [{0:s}]. Timeout set to {1:d}. The container ID is printed below.".format(
            self.name, self.time_out))
        utils.xrun("docker", ["start", "-a", self.name],
                       timeout=self.time_out,
                       logfile=self.logfile,
                       log=self.logger, output_wrangler=output_wrangler,
                       kill_callback=lambda: utils.xrun("docker", ["kill", self.name]))
        uptime = seconds_hms(time.time() - tstart)
        self.uptime = uptime
        self._print(
            "Container [{0}] has executed successfully".format(self.name))

        self._print("Runtime was {0}.".format(uptime))

        self.status = "exited"

    def stop(self):
        dinfo = self.info()
        status = dinfo["State"]["Status"]
        killed = False
        if status in ["running", "paused"]:
            try:
                utils.xrun("docker stop", [self.name])
            except KeyboardInterrupt("Received terminate signal. Will stop and remove container first"):
                killed = True
        self.status = 'exited'

        self._print("Container {} has been stopped.".format(self.name))
        if killed:
            self.remove()
            raise KeyboardInterrupt

    def image_exists(self):
        """
            Check if image exists 
        """
        image_ids = subprocess.check_output(f"docker images -q {self.image}".split())
        if image_ids:
            return True
        else:
            return False

    def remove(self):
        dinfo = self.info()
        status = dinfo["State"]["Status"]
        killed = False
        if status == "exited":
            try:
                utils.xrun("docker rm", [self.name])
            except KeyboardInterrupt:
                killed = True
            if killed:
                raise KeyboardInterrupt

        else:
            raise DockerError(
                "Container [{}] has not been stopped, cannot remove".format(self.name))

        self.cont_logger.remove('containers', self.name)
        self.cont_logger.write()

    def _print(self, message):
        if self.logger:
            self.logger.info(message)
        else:
            print(message)
