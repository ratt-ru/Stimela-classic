## Dockerized reduction srcipt framework for radio astronomy
# Sphesihle Makhathini <sphemakh@gmail.com>

import os
import sys
from otrera import penthesilea_docker as docker
import otrera.utils as utils
import penthesilea
import tempfile
import time


ekhaya = penthesilea.__path__[0]

CONFIGS_ = {
    "ares/simms" : "{:s}/configs/simms_params.json".format(ekhaya),
    "ares/simulator" : "{:s}/configs/simulator_params.json".format(ekhaya),
    "ares/imager" : "{:s}/configs/imager_params.json".format(ekhaya),
    "ares/predict" : "{:s}/configs/simulator_params.json".format(ekhaya),
    "ares/calibrator" : "{:s}/configs/calibrator_params.json".format(ekhaya),
    "ares/sourcery" : "{:s}/configs/sourcery_params.json".format(ekhaya),
    "ares/flagms" : "{:s}/configs/flagms_params.json".format(ekhaya),
    "ares/autoflagger" : "{:s}/configs/autoflagger_params.json".format(ekhaya),
    "ares/subtract" : "{:s}/configs/subtract_params.json".format(ekhaya)
}


class Pipeline(object):

    def __init__(self, name, configs, data, ms_dir=None, mac_os=False):
        
        self.name = name
        self.log = utils.logger(0,
                   logfile="log-%s.txt"%name.replace(" ","_").lower())

        self.containers = []
        self.active = None
        self.configs_path = configs
        self.data_path = data
        self.configs_path_container = "/configs"
        self.otrera_path = os.path.dirname(docker.__file__)
        self.MAC_OS = mac_os

        self.ms_dir = ms_dir
        if ms_dir:
            if not os.path.exists(ms_dir):
                os.mkdir(ms_dir)


    def add(self, image, name, config,
            input=None, output=None, label="", 
            build_first=False, build_dest=None,
            saveconf=None, add_time_stamp=True):

        if build_first and build_dest:
            self.build(image, build_dest)

        if add_time_stamp:
            name = "%s-%s"%(name, str(time.time()).replace(".",""))

        cont = docker.Load(image, name, label=label, logger=self.log)

        cont.add_environ("MAC_OS", str(self.MAC_OS))

        # add standard volumes
        cont.add_volume(self.otrera_path, "/utils", perm="ro")
        cont.add_volume(self.data_path, "/data", perm="ro")

        if self.ms_dir:
            cont.add_volume(self.ms_dir, "/msdir")
            cont.add_environ("MSDIR", "/msdir")

        if input:
            cont.add_volume( input,"/input")
            cont.add_environ("INPUT", "/input")

        if output:
            if not os.path.exists(output):
                os.mkdir(output)

            cont.add_volume(output, "/output")
            cont.add_environ("OUTPUT", "/output")

        if isinstance(config, dict):
            if not os.path.exists("configs"):
                os.mkdir("configs")

            if not saveconf:
                saveconf = "configs/%s-%s.json"%(self.name.replace(" ", "_").lower(), name)

            confname_container = "%s/%s"%(self.configs_path_container, 
                        os.path.basename(saveconf))


            template = utils.readJson(CONFIGS_[image])
            template.update(config)
            utils.writeJson(saveconf, template)

            config = confname_container
            cont.add_volume("configs", self.configs_path_container, perm="ro")
        else:
            cont.add_volume(self.configs_path, self.configs_path_container, perm="ro")
            config = self.configs_path_container+"/"+config 

        cont.add_environ("CONFIG", config)

        self.containers.append(cont)


    def run(self, *args):
        """
            Run pipeline
        """

        if args:
            containers = [ self.containers[i-1] for i in args[:len(self.containers)]]
        else:
            containers = self.containers

        for i, container in enumerate(containers):
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

        self.rm(containers)
        

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


    def rm(self, containers=None):
        """
            Remove all stopped containers
        """
        for container in containers or self.containers:
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
