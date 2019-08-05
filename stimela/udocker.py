import subprocess
import os
import sys
from io import StringIO
from stimela import utils
import json
import stimela
import time
import datetime
import tempfile


class DockerError(Exception):
    pass

def pull(image, tag=None, force=False):
    """ pull a docker image """
    if tag:
        image = ":".join([image, tag])

    utils.xrun("udocker", ["pull", image])


def seconds_hms(seconds):
    return str(datetime.timedelta(seconds=seconds))


class Container(object):
    def __init__(self, image, name, 
                 volumes=None, environs=None,
                 label="", logger=None, 
                 shared_memory="1gb",
                 time_out=-1,
                 log_container=None,
                 COMMAND="",
                 use_graphics=False):
        """
        Python wrapper to docker engine tools for managing containers.
        """
  
        self.image = image
        self.name = name
        self.label = label
        self.volumes = volumes or []
        self.environs = environs or []
        self.logger = logger
        self.status = None
        self.WORKDIR = None
        self.COMMAND = COMMAND
        self.PID = os.getpid()
        self.uptime = "00:00:00"
        self.time_out = time_out
        self.use_graphics = use_graphics
        self.cont_logger = utils.logger.StimelaLogger(log_container or stimela.LOG_FILE, jtype="udocker")


    def  add_volume(self, host, container, noverify=False):

        if os.path.exists(host) or noverify:
            if self.logger:
                self.logger.debug("Mounting volume [{0}] in container [{1}] at [{2}]".format(host, self.name, container))
            host = os.path.abspath(host)
        else:
            raise IOError("Directory {0} cannot be mounted on container: File doesn't exist".format(host))
      
        self.volumes.append(":".join([host,container]))


    def add_environ(self, key, value):
        if self.logger:
            self.logger.debug("Adding environ varaible [{0}={1}] in container {2}".format(key, value, self.name))
        self.environs.append('"{0:s}={1:s}"'.format(key, value))


    def run(self, *args):

        if self.volumes: 
            volumes = " --volume=" + " --volume=".join(self.volumes)
        else:
            volumes = ""
        if self.environs:
            environs = environs = " --env="+" --env=".join(self.environs)
        else:
            environs = ""
      
        self._print("Running container [{}]".format(self.name))
        tstart = time.time()
        utils.xrun("udocker run", ["=".join(args)] + [volumes, environs,
                        "--workdir=%s"%(self.WORKDIR) if self.WORKDIR else "",
                        "--rm",
                        "--dri" if self.use_graphics else "",
                        self.name, self.COMMAND or ""], timeout=self.time_out)

        self.status = "running"
        uptime = seconds_hms(time.time() - tstart)
        self.uptime = uptime
        self._print("Runtime was {0}.".format(uptime))


    def info(self):

        output = subprocess.check_output("udocker inspect {}".format(self.name), shell=True).decode()
        output_file = StringIO(output[3:-3])
        jdict = json.load(output_file)
        output_file.close()

        return jdict
  
  
    def get_log(self):
        stdout = open(self.logfile, 'w')
        exit_status = subprocess.call("docker logs {0}".format(self.name),
                            stdout=stdout, stderr=stdout, shell=True)
        if exit_status !=0:
            self.logger.warn('Could not log container: {}. Something went wrong durring execution'.format(self.name))
            output = 'Task was not started.'
            stdout.write(output)
        else:
            output = stdout.read()

        stdout.close()
        return output

      
    def create(self):
        running = True
        self.status = "created"
      
        #self.cont_logger.log_container(self.name)
        #self.cont_logger.write()
        self._print("Creating container [{0:s}]. Timeout set to {1:d}. The container ID is printed below.".format(self.name, self.time_out))
        utils.xrun("udocker", ["create", "--name={0:s}".format(self.name), self.image])

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


    def remove(self):
        dinfo = self.info()
        status = dinfo["State"]["Status"]
        killed = False
        if status == "exited":
            try:
                utils.xrun("udocker rm", [self.name])
            except KeyboardInterrupt:
                killed = True
            if killed:
                raise KeyboardInterrupt
         
        else:
            raise DockerError("Container [{}] has not been stopped, cannot remove".format(self.name))

#        self.cont_logger.remove('containers', self.name)
#        self.cont_logger.write()

    def _print(self, message):
        if self.logger:
            self.logger.info(message)
        else:
            print(message)
