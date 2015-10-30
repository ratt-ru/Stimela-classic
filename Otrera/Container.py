## Simple interface to Docker containers
# Sphesihle Makhathini <sphemakh@gmail.com>

from Otrera import utils

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
            utils._run("docker", ["run",
                 volumes, environs,
                 "--name", self.name, 
                 self.image])
        except SystemError:
            raise DockerError("Container [%s:%s] returned non-zero exit status"%(self.image, self.name))

    
    def stop(self):
        utils._run("test", ["`docker inspect -f {{.State.Running}} %s`"%self.name,
                         "&&", "docker stop", self.name])

    def rm(self):
        utils._run("docker", ["rm", self.name])


    def pause(self):
        utils._run("test", ["`docker inspect -f {{.State.Running}} %s`"%self.name,
                         "&&", "docker pause", self.name])

    def resume(self):
        utils._run("test", ["`docker inspect -f {{.State.Running}} %s`"%self.name,
                         "&&", "docker unpause", self.name])
