## Interface to Docker engine
# Sphesihle Makhathini <sphemakh@gmail.com>

import stimela.utils as utils
import os
import time
from stimela.utils import stimela_logger
import logging


class DockerError(Exception):
    pass


def build(image, build_path, tag=None):
    """ build a docker image"""

    if tag:
        image = ":".join([image, tag])
    try:
        utils.xrun("docker build", ["-t", image, 
                    build_path])
    except SystemError:
        raise DockerError("Container [{:s}] returned non-zero exit status".format(image))

 
def pull(image, tag=None):
    """ pull a docker image """

    if tag:
        image = ":".join([image, tag])
    try:
        utils.xrun("docker pull", [image])
    except SystemError:
        raise DockerError("Container [{:s}] returned non-zero exit status".format(image))


def stop_container(container):
    print "STOPING"
    utils.xrun("test", ["`docker inspect -f {{.State.Running}} {:s}`".format(container),
                         "&&", "docker stop", container])


def rm_container(container):
    try:
        utils.xrun("docker", ["rm", container])
    except SystemError:
        raise DockerError("Could not remove stopped contianer [{:s}].\
It may be still running or it doesn't exist".format(container))
  

class Load(object):

    def __init__(self, image, name, INPUT, OUTPUT, 
                 volumes=None, environs=None,
                 label="", awsEC2=False, logger=None):
    
        self.image = image
        self.name = name
        self.label = label
        self.volumes = volumes or []
        self.INPUT = INPUT
        self.OUTPUT = OUTPUT
        self.environs = environs or []
        self.awsEC2 = awsEC2
        self.logger = logger
        self.started = False
        self.WORKDIR = None
        self.COMMAND = None


    def  add_volume(self, host, container, perm="rw"):

        if os.path.exists(host):
            if self.logger:
                self.logger.debug("Mounting volume [%s] in container [%s] at [%s]"%(host, self.name, container))
            host = os.path.abspath(host)
        else:
            raise IOError("Directory [%s] cannot be mounted on container: File doesn't exist"%host)
        
        self.volumes.append(":".join([host,container,perm]))


    def add_environ(self, key, value):
        if self.logger:
            self.logger.debug("Adding environ varaible [%s=%s] in container [%s]"%(key, value, self.name))
        self.environs.append("=".join([key, value]))


    def configure_EC2(self, cpu=8, ram=64):
        """
            Run container on a customized AWS EC2 instance

            ** Not implemented yet **
        """
        self.EC2_cpu = cpu
        self.EC2_ram = ram


    def start(self, logfile=None, shared_memory=1024):
        
        logging.basicConfig(filename="%s/log-%s.txt"%(self.OUTPUT, self.name))
        stderrLogger = logging.StreamHandler()
        stderrLogger.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
        logging.getLogger().addHandler(stderrLogger)

        volumes = " -v " + " -v ".join(self.volumes)
        environs = " -e "+" -e ".join(self.environs)

        self.started = True

        if self.awsEC2:
            pass
        try:
            utils.xrun("docker", ["run",
                 volumes, environs,
                 "-w %s"%(self.WORKDIR) if self.WORKDIR else "",
                 "--name", self.name, "--shm-size=%dMB"%shared_memory,
                 self.image,
                 self.COMMAND or ""],
                 _log_container_as_started=self, logfile=logfile)

        except SystemError:
            raise DockerError("Container [%s:%s] returned non-zero exit status"%(self.image, self.name))
            if logfile:
                self.log(action="failed", logfile=logfile)

        self.log(action="stop", logfile=logfile)

    
    def stop(self, logfile=None):

        stop_container(self.name)

        if logfile:
            self.log(action="start", logfile=logfile)


    def rm(self, logfile=None):

        if not self.started :
            self.logger.info("Container [%s] was not started. Will not not attempt to remove"%(self.name))
            return

        try:
            rm_container(self.name)
        except DockerError:
            message = "Could not remove stopped contianer [%s].\
It may be still running or it doesn't exist"%(self.name)

            if self.logger:
                self.logger.debug(message)
            else:
                print message

        if logfile:
            self.log(action="rm", logfile=logfile)


    def pause(self):
        utils.xrun("test", ["`docker inspect -f {{.State.Running}} %s`"%self.name,
                         "&&", "docker pause", self.name])

    def resume(self):
        utils.xrun("test", ["`docker inspect -f {{.State.Running}} %s`"%self.name,
                         "&&", "docker unpause", self.name])

    def status(self):
        import subprocess
    
        xrun = lambda cmd: subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, shell=True)
    
        status_ = xrun("docker inspect -f {{.State.Status}} " + self.name)
        cont_id = xrun("docker inspect -f {{.Id}} " + self.name)
        started = xrun("docker inspect -f {{.State.StartedAt}} " + self.name)
    
        out_status = status_.stdout.read()
        err_status = status_.stderr.read()

        if err_status:
            raise DockerError("Could not inspect container [{:s}]. {:s}".format(self.name, err_status))
    
        out_id = cont_id.stdout.read()[:12]

        out_started = started.stdout.read().split(".")[0]

        started_tuple = time.strptime(out_started, "%Y-%m-%dT%H:%M:%S")
        started = time.mktime(started_tuple)

        if out_status.find("running")<0:
            stopped = xrun("docker inspect -f {{.State.FinishedAt}} " + self.name)
            out_stopped = stopped.stdout.read().split(".")[0]
            stopped_tuple = time.strptime(out_stopped, "%Y-%m-%dT%H:%M:%S")
            stopped = time.mktime(stopped_tuple)

        else:
            stopped = time.time()

        uptime = (stopped - started)
        h = (uptime - uptime%3600)
        m = uptime - h
        m -= m%60
        s = uptime - (h + m)
        uptime = "{:d}:{:d}:{:d}".format(int(h/3600), int(m/3600), int(s))

        err_id = cont_id.stderr.read()

        return out_status.strip(), out_id.strip(), uptime


    def log(self, action, logfile, status=None, _id=None):
        """
            Actions are: start, stop, rm, clear
            The logfile must exist. 
        """
        if action in ["start", "stop"]:
            status, _id, uptime = self.status()

        # open file
        conts = stimela_logger.Container(logfile)

        if action=="start":
            conts.add( dict(name=self.name, id=_id,uptime= uptime, pid=os.getpid(), status=status) )

        elif action in ["stop", "rm", "clear"]:
            if conts.lines:
                pass
            else:
                raise ValueError("Action [{:s}] cannot be perfomed. There are no logged containers".format(self.name))

            if action=="stop":
                conts.update(self.name, status="exited")
            elif action=="failed":
                conts.update(self.name, status="failed")
            elif action=="rm":
                conts.rm(self.name)

        else:
            raise ValueError("action [{:s}] is not understood. Allowed actions are [start, stop, rm, clear]".format(action))
        
        conts.write() 
