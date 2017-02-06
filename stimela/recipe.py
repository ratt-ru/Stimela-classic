import os
import sys
import time
import stimela
from stimela import docker, utils, cargo
from stimela.cargo import cab
import logging
import inspect
import re

USER = os.environ["USER"]
UID = os.getuid()
CAB_PATH = os.path.abspath(os.path.dirname(cab.__file__))


class PipelineException(Exception):
    """ 
    Encapsulates information about state of pipeline when an
    exception occurs
    """
    def __init__(self, exception, completed, failed, remaining):
        message = ("Exception occurred while running "
            "pipeline component '%s': %s" % (failed.label, str(exception)))

        super(PipelineException, self).__init__(message)

        self._completed = completed
        self._failed = failed
        self._remaining = remaining

    @property
    def completed(self):
        return self._completed

    @property
    def failed(self):
        return self._failed

    @property
    def remaining(self):
        return self._remaining


class Recipe(object):
    def __init__(self, name, data=None,
                 parameter_file_dir=None, ms_dir=None,
                 tag=None, loglevel='INFO'):
        """
        Deifine and manage a stimela recipe instance.        

        name    :   Name of stimela recipe
        data    :   Path of stimela data. The data is assumed to be at Stimela/stimela/cargo/data
        msdir   :   Path of MSs to be used during the execution of the recipe
        tag     :   Use cabs with a specific tag
        parameter_file_dir :   Will store task specific parameter files here
        """

        self.log = logging.getLogger('STIMELA')
        self.log.setLevel(getattr(logging, loglevel))
        # create file handler which logs even debug
        # messages
        name_ = name.lower().replace(' ', '_')
        self.logfile = 'log-{}.txt'.format(name_)
        self.resume_file = '.last_{}.json'.format(name_)

        fh = logging.FileHandler(self.logfile)
        fh.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.ERROR)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
        # add the handlers to logger
        self.log.addHandler(ch)
        self.log.addHandler(fh)


        self.stimela_context = inspect.currentframe().f_back.f_globals

        self.stimela_path = os.path.dirname(docker.__file__)

        self.name = name
        self.ms_dir = ms_dir
        if not os.path.exists(self.ms_dir):
            self.log.info('MS directory \'{}\' does not exist. Will create it'.format(self.ms_dir))
            os.mkdir(self.ms_dir)
        self.tag = tag
        # create a folder to store config files
        # if it doesn't exist. These config
        # files can be resued to re-run the
        # task
        self.parameter_file_dir = parameter_file_dir or "stimela_parameter_files"
        if not os.path.exists(self.parameter_file_dir):
            self.log.info('Config directory not be found. Will create ./{}'.format(self.parameter_file_dir))
            os.mkdir(self.parameter_file_dir)

        self.containers = []
        self.completed = []
        self.failed = None
        self.remaining = []

        self.proc_logger = utils.logger.StimelaLogger(stimela.LOG_FILE)
        self.pid = os.getpid()
        self.proc_logger.log_process(self.pid, self.name)
        self.proc_logger.write()


    def add(self, image, name=None, config=None,
            input=None, output=None, msdir=None,
            label=None, shared_memory='1gb'):
        """
        Add a task to a stimela recipe

        image   :   stimela cab name, e.g. 'cab/simms'
        name    :   This name will be part of the name of the contaier that will 
                    execute the task (now optional)
        config  :   Dictionary of options to parse to the task. This will modify 
                    the parameters in the default parameter file which 
                    can be viewd by running 'stimela cabs -i <cab name>', e.g 'stimela cabs -i simms'
        input   :   input dirctory for cab
        output  :   output directory for cab
        msdir   :   MS directory for cab. Only specify if different from recipe ms_dir
        """

        # check if name has any offending charecters
        offenders = re.findall('\W', name)
        if offenders:
            raise ValueError('The cab name \'{:s}\' has some non-alphanumeric characters.'
                             ' Charecters making up this name must be in [a-z,A-Z,0-9,_]'.format(name))
        # Get location of template parameters file
        parameter_file = '{0}/{1}/parameters.json'.format(CAB_PATH, image.split('/')[-1].split(':')[0])
        msdir = msdir or self.ms_dir
        
        if name is None:
            name = '{0}_{1}-{2}{3}'.format(USER, image, id(image), str(time.time()).replace('.', ''))
        else:
            name = '{0}-{1}{2}'.format(name, id(image), str(time.time()).replace('.', ''))

        _cab = cab.CabDefinition(indir=input, outdir=output,
                    msdir=msdir, parameter_file=parameter_file)
         


        # Volumes to be mounted into the container
        input = input or self.stimela_context.get('STIMELA_INPUT', None)
        output = output or self.stimela_context.get('STIMELA_OUTPUT', None)

        cont = docker.Container(image, name,
                     label=label, logger=self.log,
                     shared_memory=shared_memory, log_container=stimela.LOG_FILE)

        
#        parameter_file_name = '{0}/{1}.json'.format(self.parameter_file_dir, name)
#        _cab.update(config, parameter_file_name)
        
        # Container parameter file will be updated and validated before the container is executed
        cont._cab = _cab
        cont.parameter_file_name = '{0}/{1}.json'.format(self.parameter_file_dir, name)
        cont.config = config

        # These are standard volumes and
        # environmental variables. These will be
        # always exist in a cab container
        cont.add_volume(self.stimela_path, '/utils', perm='ro')
        cont.add_volume(self.parameter_file_dir, '/configs', perm='ro')
        cont.add_environ('CONFIG', '/configs/{}.json'.format(name))

        if msdir:
            md = '/home/%s/msdir'%USER
            cont.add_volume(msdir, md)
            cont.add_environ('MSDIR', md)
            # Keep a record of the content of the
            # volume
            dirname, dirs, files = [a for a in next(os.walk(msdir))]
            cont.msdir_content = {
                "volume"    :   dirname,
                "dirs"      :   dirs,
                "files"     :   files,
            }

            self.log.debug('Mounting volume \'{0}\' from local file system to \'{1}\' in the container'.format(msdir, md))

        if input:
            cont.add_volume( input,'/input', perm='ro')
            cont.add_environ('INPUT', '/input')
            # Keep a record of the content of the
            # volume
            dirname, dirs, files = [a for a in next(os.walk(input))]
            cont.input_content = {
                "volume"    :   dirname,
                "dirs"      :   dirs,
                "files"     :   files,
            }

            self.log.debug('Mounting volume \'{0}\' from local file system to \'{1}\' in the container'.format(input, '/input'))

        if output:
            if not os.path.exists(output):
                os.mkdir(output)
            od = '/home/%s/output'%USER
            cont.add_volume(output, od)
            cont.add_environ('OUTPUT', od)
            cont.logfile = '{0}/log-{1}.txt'.format(output, name.split('-')[0])
            self.log.debug('Mounting volume \'{0}\' from local file system to \'{1}\' in the container'.format(output, od))

        cont.image = '{0}_{1}'.format(USER, image)
        self.log.info('Adding cab \'{0}\' to recipe. The container will be named \'{1}\''.format(cont.image, name))
        self.containers.append(cont)


    def log2recipe(self, cont, recipe, num, status):

        step = {
                "name"          :   cont.name,
                "number"        :   num,
                "cab"           :   cont.image,
                "volumes"       :   cont.volumes,
                "environs"      :   cont.environs,
                "shared_memory" :   cont.shared_memory,
                "input_content" :   cont.input_content,
                "msdir_content" :   cont.msdir_content,
                "label"         :   cont.label,
                "status"        :   status,
        }
        recipe['steps'].append(step)


    def run(self, steps=None, resume=False, redo=None):
        """
        Run a Stimela recipe. 

        steps   :   recipe steps to run
        resume  :   resume recipe from last run
        redo    :   Re-run an old recipe from a .last file
        """

        recipe = {
            "name"      :   self.name,
            "steps"     :   []
        }
        start_at = 0

        if redo:
            recipe = utils.readJson(redo)
            self.log.info('Rerunning recipe {0} from {1}'.format(recipe['name'], redo))
            self.log.info('Recreating recipe instance..')
            self.containers = []
            for step in recipe['steps']:
                
            #        add I/O folders to the json file
            #        add a string describing the contents of these folders
            #        The user has to ensure that these folders exist, and have the required content
                
                self.log.info('Adding cab \'{0}\' to recipe. The container will be named \'{1}\''.format(step['cab'], step['name']))
                cont = docker.Container(step['cab'], step['name'],
                                      label=step['label'], logger=self.log,
                                      shared_memory=step['shared_memory'])
                self.log.debug('Adding volumes {0} and environmental variables {1}'.format(step['volumes'], step['environs']))
                cont.volumes = step['volumes']
                cont.environs = step['environs']
                cont.shared_memory = step['shared_memory']
                cont.input_content = step['input_content']
                cont.msdir_content = step['msdir_content']

                self.containers.append(cont)

        elif resume:
            self.log.info("Resuming recipe from last run.")
            try:
                recipe = utils.readJson(self.resume_file)
            except IOError:
                raise IOError("Cannot resume pipeline, resume file '{}' not found".format(self.resume_file))

            steps_ = recipe.pop('steps')
            recipe['steps'] = []
            _steps = []
            for step in steps_:
                if step['status'] == 'completed':
                    recipe['steps'].append(step)
                    continue

                _cab = step['cab']
                number = step['number']

                if _cab == self.containers[number-1].image:
                    self.log.info('recipe step \'{0}\' is fit for re-execution. CAB = {1}'.format(number, _cab))
                    _steps.append(number)
                else:
                    raise RuntimeError('Recipe flow, or task scheduling has changed. Cannot resume recipe. CAB= {0}'.format(_cab))
            if len(_steps)==0:
                self.log.info('All the steps were completed. No steps to resume')
                sys.exit(0)
            steps = _steps

        if getattr(steps, '__iter__', False):
            _steps = []
            if isinstance(steps[0], str):
                labels = [ cont.label.split('::')[0] for cont in self.containers]

                for step in steps:
                    try:
                        _steps.append(labels.index(step)+1)
                    except ValueError:
                        raise ValueError('Recipe label ID [{0}] doesn\'t exist'.format(step))
                steps = _steps
        else:
            steps = range(1, len(self.containers)+1)


        containers = [(step, self.containers[step-1]) for step in steps]        

        for i, (step, container) in enumerate(containers):
            created = False
            try:
                # Update container parameter file if need be
                if hasattr(container, '_cab'):
                    container._cab.update(container.config, container.parameter_file_name)

                self.log.info('Running Container {}'.format(container.name))
                self.log.info('STEP {0} :: {1}'.format(i+1, container.label))
                self.active = container

                container.create()
                created = True
                container.start()
                self.log2recipe(container, recipe, step, 'completed')
            except BaseException as e:
                self.completed = [cont[1] for cont in containers[:i]]
                self.remaining = [cont[1] for cont in containers[i+1:]]
                self.failed = container

                self.log.info('Recipe execution failed while running container {}'.format(container.name))
                self.log.info('Completed containers : {}'.format([c.name for c in self.completed]))
                self.log.info('Remaining containers : {}'.format([c.name for c in self.remaining]))

                self.log2recipe(container, recipe, step, 'failed')
                for step, cont in containers[i+1:]:
                    self.log.info('Logging remaining task: {}'.format(cont.label or cont.name))
                    self.log2recipe(cont, recipe, step, 'remaining')

                self.log.info('Saving pipeline information in {}'.format(self.resume_file))
                utils.writeJson(self.resume_file, recipe)

                pe = PipelineException(e, self.completed, container, self.remaining)

                raise pe, None, sys.exc_info()[2]
            finally:
                container.get_log()
                if created:
                    container.stop()
                    container.remove()
                self.proc_logger.remove('processes', self.pid)
                self.proc_logger.write()

        self.log.info('Saving pipeline information in {}'.format(self.resume_file))
        utils.writeJson(self.resume_file, recipe)

        self.log.info('Recipe executed successfully')
