# -*- coding: future_fstrings -*-
import subprocess
import os
import sys
from stimela import utils
from stimela.cargo import cab
import json
import stimela
import time
import datetime
import tempfile
import hashlib
from shutil import which

binary = which("singularity")
if binary:
    __version_string = subprocess.check_output([binary, "--version"]).decode("utf8")
    version = __version_string.strip().split()[-1]
    if version < "3.0.0":
        suffix = ".img"
    else:
        suffix = ".sif"
else:
    version = None

class SingularityError(Exception):
    pass


def make_overlay(name, directory, size=5):
    """
    Make overlay file system
    """

    upper = os.path.join(directory, "overlay", "upper")
    overlay = os.path.join(directory, "overlay")
    name = os.path.join(directory, name)
    os.makedirs(upper, exist_ok=True)
    utils.xrun("dd", f"if=/dev/zero of={name} bs=1M count={size} && \
                mkfs.ext3 -d {overlay} {name}".split())
    return name

def pull(image, store_path, docker=True, directory=".", force=False):
    """ 
        pull an image
    """
    if docker:
        fp = "docker://{0:s}".format(image)
    else:
        fp = image
    if not os.path.exists(directory):
        os.mkdir(directory)

    utils.xrun("singularity", ["build", 
        	"--force" if force else "", 
         	os.path.join(directory,store_path), fp])

    return 0


class Container(object):
    def __init__(self, image, name,
                 volumes=None,
                 logger=None,
                 time_out=-1,
                 runscript="/singularity",
                 environs=None,
                 workdir=None):
        """
        Python wrapper to singularity tools for managing containers.
        """

        self.image = image
        self.volumes = volumes or []
        self.environs = environs or []
        self.logger = logger
        self.status = None
        self.WORKDIR = workdir
        self.RUNSCRIPT = runscript
        self.PID = os.getpid()
        self.uptime = "00:00:00"
        self.time_out = time_out

        hashname = hashlib.md5(name.encode('utf-8')).hexdigest()[:3]
        self.name = hashname if version < "3.0.0" else name

    def add_volume(self, host, container, perm="rw", noverify=False):
        if os.path.exists(host) or noverify:
            if self.logger:
                self.logger.debug("Mounting volume [{0}] in container [{1}] at [{2}]".format(
                    host, self.name, container))
            host = os.path.abspath(host)
        else:
            raise IOError(
                "Path {0} cannot be mounted on container: File doesn't exist".format(host))

        self.volumes.append(":".join([host, container, perm]))

        return 0

    def add_environ(self, key, value):
        self.logger.debug("Adding environ varaible [{0}={1}] "\
                    "in container {2}".format(key, value, self.name))
        self.environs.append("=".join([key, value]))
        key_ = f"SINGULARITYENV_{key}"
	
        self.logger.debug(f"Setting singularity environmental variable {key_}={value} on host")
        os.environ[key_] = value

        return 0

    def run(self, *args):
        """
        Run a singularity container instance
        """

        if self.volumes:
            volumes = " --bind " + " --bind ".join(self.volumes)
        else:
            volumes = ""

        if not os.path.exists(self.image):
            self.logger.error(f"The image, {self.image}, required to run this cab does not exist."\
                    " Please run 'stimela pull --help' for help on how to download the image")
            raise SystemExit from None

        if hasattr(self, "overlay"):
            args = list(args)
            args.append(f"--overlay {self.overlay}")
        else:
            args = list(args)

        self.status = "running"
        self._print("Starting container [{0:s}]. Timeout set to {1:d}. The container ID is printed below.".format(
            self.name, self.time_out))
        utils.xrun(f"cd {self.workdir_host} && singularity", ["run", "--workdir", self.workdir_host] \
                    + args + [volumes, self.image, self.RUNSCRIPT],
                    log=self.logger, timeout=self.time_out, 
                    logfile=self.logfile)

        self.status = "exited"

        return 0


    def _print(self, message):
        if self.logger:
            self.logger.info(message)
        else:
            print(message)

        return 0
