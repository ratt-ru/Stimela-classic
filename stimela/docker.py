import subprocess
import os
import sys
from cStringIO import StringIO as io
from stimela import utils
import json
import stimela
import time
import datetime
import tempfile

class DockerError(Exception):
    pass


def build(image, build_path, tag=None, build_args=None, fromline=None, args=[]):
    """ build a docker image"""

    if tag:
        image = ":".join([image, tag])

    bdir = tempfile.mkdtemp()
    os.system('cp -r {0:s}/* {1:s}'.format(build_path, bdir))
    if build_args:
        stdw = tempfile.NamedTemporaryFile(dir=bdir)
        with open("{}/Dockerfile".format(bdir)) as std:
            dfile = std.readlines()

        for line in dfile:
            if fromline and line.lower().startswith('from'):
                stdw.write('FROM {:s}\n'.format(fromline))
            elif line.lower().startswith("cmd"):
                for arg in build_args:
                    stdw.write(arg+"\n")
                stdw.write(line)
            else:
                stdw.write(line)
        stdw.flush()
        utils.xrun("docker build", args+["--force-rm","-f", stdw.name, 
                   "-t", image, 
                    bdir])

        stdw.close()
    else:
        utils.xrun("docker build", args+["--force-rm", "-t", image, 
                    bdir])

    os.system('rm -rf {:s}'.format(bdir))
    
def pull(image, tag=None):
    """ pull a docker image """
    if tag:
        image = ":".join([image, tag])

    utils.xrun("docker pull", [image])


def seconds_hms(seconds):
    return str(datetime.timedelta(seconds=seconds))


class Container(object):
    def __init__(self, image, name, 
                 volumes=None, environs=None,
                 label="", logger=None, 
                 shared_memory="1gb",
                 time_out=-1,
                 log_container=None):
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
        self.COMMAND = None
        self.shared_memory = shared_memory
        self.PID = os.getpid()
        self.uptime = "00:00:00"
        self.time_out = time_out
        self.cont_logger = utils.logger.StimelaLogger(log_container or stimela.LOG_FILE)


    def  add_volume(self, host, container, perm="rw"):

        if os.path.exists(host):
            if self.logger:
                self.logger.debug("Mounting volume [{0}] in container [{1}] at [{2}]".format(host, self.name, container))
            host = os.path.abspath(host)
        else:
            raise IOError("Directory {0} cannot be mounted on container: File doesn't exist".format(host))
        
        self.volumes.append(":".join([host,container,perm]))


    def add_environ(self, key, value):
        if self.logger:
            self.logger.debug("Adding environ varaible [{0}={1}] in container {2}".format(key, value, self.name))
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
        
        self._print("Instantiating container [{}]. The container ID is printed below.".format(self.name))
        utils.xrun("docker create", list(args) + [volumes, environs,
                        "-w %s"%(self.WORKDIR) if self.WORKDIR else "",
                        "--name", self.name, "--shm-size", self.shared_memory,
                        self.image,
                        self.COMMAND or ""])

        self.status = "created"

    def info(self):

        output = subprocess.check_output("docker inspect {}".format(self.name), shell=True)
        output_file = io(output[3:-3])
        jdict = json.load(output_file)
        output_file.close()

        return jdict
    
    
    def get_log(self):
        stdout = open(self.logfile, 'a+')
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

        
    def start(self):
        running = True
        tstart = time.time()
        self.status = "running"
        
        self.cont_logger.log_container(self.name)
        self.cont_logger.write()
        try:
            self._print("Starting container [{0:s}]. Timeout set to {1:d}. The container ID is printed below.".format(self.name, self.time_out))
            utils.xrun("docker", ["start", "-a", self.name], 
                       timeout=self.time_out, 
                       kill_callback=lambda: utils.xrun("docker", ["kill", self.name]))
        except KeyboardInterrupt:
            utils.xrun("docker", ["kill", self.name])
            raise 
           
        uptime = seconds_hms(time.time() - tstart)
        self.uptime = uptime
        self._print("Container [{0}] has executed successfully".format(self.name))

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
            raise DockerError("Container [{}] has not been stopped, cannot remove".format(self.name))

        self.cont_logger.remove('containers', self.name)
        self.cont_logger.write()

    def _print(self, message):
        if self.logger:
            self.logger.info(message)
        else:
            print(message)
