import subprocess
import os
import sys
from stimela import utils
import json
import stimela
import time
import datetime
import tempfile
import hashlib


class SingularityError(Exception):
    pass


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
    utils.xrun("cd", [directory, "&&", "singularity", "pull", "--force" if force else "",
                      "--name", store_path, fp])

    return 0


class Container(object):
    def __init__(self, image, name,
                 volumes=None,
                 logger=None,
                 time_out=-1,
                 runscript=""):
        """
        Python wrapper to singularity tools for managing containers.
        """

        self.image = image
        self.name = hashlib.md5(name.encode('utf-8')).hexdigest()[:3]
        self.volumes = volumes or []
        self.logger = logger
        self.status = None
        self.WORKDIR = None
        self.RUNSCRIPT = runscript
        self.PID = os.getpid()
        self.uptime = "00:00:00"
        self.time_out = time_out
        #self.cont_logger = utils.logger.StimelaLogger(log_container or stimela.LOG_FILE)

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

    def start(self, *args):
        """
        Create a singularity container instance
        """

        if self.volumes:
            volumes = " --bind " + " --bind ".join(self.volumes)
        else:
            volumes = ""

        self._print("Instantiating container [{0:s}]. Timeout set to {1:d}. The container ID is printed below.".format(
            self.name, self.time_out))
        utils.xrun("singularity instance.start",
                   list(args) + [volumes,
                                 "-c",
                                 self.image, self.name])

        self.status = "created"

        return 0

    def run(self, *args):
        """
        Run a singularity container instance
        """

        if self.volumes:
            volumes = " --bind " + " --bind ".join(self.volumes)
        else:
            volumes = ""

        self._print("Starting container [{0:s}]. Timeout set to {1:d}. The container ID is printed below.".format(
            self.name, self.time_out))
        utils.xrun("singularity run", ["instance://{0:s} {1:s}".format(self.name, self.RUNSCRIPT)],
                   logfile=list(filter(lambda x: "log" in x, self.volumes))[0].split(":")[0],
                   timeout=self.time_out, kill_callback=self.stop)

        self.status = "running"

        return 0

    def stop(self, *args):
        """
        Stop a singularity container instance
        """

        if self.volumes:
            volumes = " --bind " + " --bind ".join(self.volumes)
        else:
            volumes = ""

        self._print(
            "Stopping container [{}]. The container ID is printed below.".format(self.name))
        utils.xrun("singularity", ["instance.stop {0:s}".format(self.name)])

        self.status = "exited"

        return 0

    def _print(self, message):
        if self.logger:
            self.logger.info(message)
        else:
            print(message)

        return 0
