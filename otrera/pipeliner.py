## Dockerized reduction srcipt framework for radio astronomy
# Sphesihle Makhathini <sphemakh@gmail.com>

import os
from otrera import penthesilea_docker as docker
import otrera.utils as utils

class Pipeline(object):

    def __init__(self, name, configs, data, ms_dir=None):
        
        self.name = name
        self.log = utils.logger(0)

        self.containers = []
        self.active = None
        self.configs_path = configs
        self.data_path = data
        self.configs_path_container = "/configs"
        self.otrera_path = os.path.dirname(docker.__file__)

        self.ms_dir = ms_dir
        if ms_dir:
            if not os.path.exists(ms_dir):
                os.mkdir(ms_dir)


    def add(self, image, name, config, 
            input=None, output=None, label="", 
            build_first=False, build_dest=None):

        if build_first and build_dest:
            self.build(image, build_dest)

        cont = docker.Load(image, name, label=label)
        cont.add_volume(self.otrera_path, "/utils")
        cont.add_volume(self.configs_path, self.configs_path_container)
        cont.add_volume(self.data_path, "/data")
        if self.ms_dir:
            cont.add_volume(self.ms_dir, "/msdir")

        if input:
            cont.add_volume( input,"/input")
            cont.add_environ("INPUT", "/input")

        if output:
            if not os.path.exists(output):
                os.mkdir(output)

            cont.add_volume(output, "/output")
            cont.add_environ("OUTPUT", "/output")

        if isinstance(config, dict):
            confname_host = "%s/%s_config.json"%(self.configs_path, name)
            confname_container = "%s/%s_config.json"%(self.configs_path_container, name)
            utils.writeJson(confname_host, config)
            config = confname_container
        else:
            config = self.configs_path_container+"/"+config 
        cont.add_environ("CONFIG", config)

        self.containers.append(cont)


    def run(self):
        """
            Run pipeline
        """

        for i, container in enumerate(self.containers):
            self.log.info("Running Container %s"%container.name)
            self.log.info("STEP %d :: %s"%(i, container.label))
            self.active = container
            try:
                container.start()
            except docker.DockerError:
                self.rm()
                raise docker.DockerError("The container [%s] failed to execute."
                                         "Please check the logs"%(container.name))
            self.active = None

        self.log.info("Pipeline [%s] ran successfully. Will now attempt to clean up dead containers "%(self.name))

        self.rm()
        

    def build(self, name, dest, use_cache=True):
        try:
            utils.xrun("docker", ["build", "-t", name,
                       "--no-cache=%s"%("false" if use_cache else "true"), 
                       dest] )
        except SystemError:
            raise docker.DockerError("Docker image failed to build")


    def stop(self):
        """
            Stop all running containers
        """
        for container in self.containers:
            container.stop()


    def rm(self):
        """
            Remove all stopped containers
        """
        for container in self.containers:
            container.rm()


    def clear(self):
        """
            Clear container list.
            This does nothing to the container instances themselves
        """
        self.containers = []


    def pause(self):
        """
            Pause current container. This effectively pauses the pipeline
        """
        if self.active:
            self.active.pause()


    def resume(self):
        """
            Resume puased container. This effectively resumes the pipeline
        """
        if self.active:
            self.active.resume()


    def readJson(self, config):
        return utils.readJson(self.configs_path+"/"+config)
    
