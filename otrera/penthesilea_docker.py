## Simple interface to Docker containers
# Sphesihle Makhathini <sphemakh@gmail.com>

import otrera.utils as utils
import os


class DockerError(Exception):
    pass

class Load(object):

    def __init__(self, image, name, 
                 volumes=None, environs=None,
                 label="", awsEC2=False, logger=None):
    
        self.image = image
        self.name = name
        self.label = label
        self.volumes = volumes or []
        self.environs = environs or []
        self.awsEC2 = awsEC2
        self.log = logger


    def  add_volume(self, host, container, perm="rw"):

        if os.path.exists(host):
            host = os.path.abspath(host)
        else:
            raise IOError("Directory [%s] cannot be mounted on container: File doesn't exist"%host)
        
        self.volumes.append(":".join([host,container,perm]))


    def add_environ(self, key, value):
        self.environs.append("=".join([key, value]))


    def configure_EC2(self, cpu=8, ram=64):
        """
            Run container on a customized AWS EC2 instance

            ** Not implemented yet **
        """
        self.EC2_cpu = cpu
        self.EC2_ram = ram


    def start(self):

        volumes = " -v " + " -v ".join(self.volumes)
        environs = " -e "+" -e ".join(self.environs)

        if self.awsEC2:
            pass
        try:
            utils.xrun("docker", ["run",
                 volumes, environs,
                 "--name", self.name, 
                 self.image])
        except SystemError:
            raise DockerError("Container [%s:%s] returned non-zero exit status"%(self.image, self.name))

    
    def stop(self):
        utils.xrun("test", ["`docker inspect -f {{.State.Running}} %s`"%self.name,
                         "&&", "docker stop", self.name])

    def rm(self):
        try:
            utils.xrun("docker", ["rm", self.name])
        except SystemError:
            self.log.debug("Could not remove stopped contianer [%s].\
It may be still running or it doesn't exist"%(self.name))


    def pause(self):
        utils.xrun("test", ["`docker inspect -f {{.State.Running}} %s`"%self.name,
                         "&&", "docker pause", self.name])

    def resume(self):
        utils.xrun("test", ["`docker inspect -f {{.State.Running}} %s`"%self.name,
                         "&&", "docker unpause", self.name])
