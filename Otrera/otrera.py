## Dockerized reduction srcipt framework for radio astronomy
# Sphesihle Makhathini <sphemakh@gmail.com>

from Otrera import Container, utils

class Define(object):

    def __init__(self, name, configs_path):
        
        self.name = name
        self.log = utils.logger(0)

        self.containers = []
        self.active = None
        self.configs_path = configs_path
        self.configs_path_container = "/input/configs"


    def add(self, image, name, config, 
            input=None, output=None, label=""):

        cont = Container.Load(image, name, label=label)

        if input:
            cont.add_volume( input,"/input")
            cont.add_environ("INPUT", "/input")

        if output:
            cont.add_volume( output,"/output")
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
            container.start()
            self.active = None


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
