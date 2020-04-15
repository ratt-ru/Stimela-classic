# -*- coding: future_fstrings -*-
import os
import sys
import time
import stimela
from stimela import docker, singularity, udocker, utils, cargo, podman, main
from stimela.cargo import cab
import logging
import inspect
import re
from stimela.exceptions import *
from stimela.dismissable import dismissable
from stimela.main import get_cabs
from stimela.cargo.cab import StimelaCabParameterError
from datetime import datetime
import traceback

version = stimela.__version__
UID = os.getuid()
GID = os.getgid()
CAB_PATH = os.path.abspath(os.path.dirname(cab.__file__))
BIN = os.path.abspath(os.path.dirname(sys.executable))

CONT_MOD = {
        "docker" : docker,
        "udocker" : udocker,
        "singularity" : singularity,
        "podman" : podman
        }

CONT_IO = cab.IODEST

WORKDIR = CONT_IO["output"]

class StimelaJob(object):
    logs_avail = dict()
    def __init__(self, name, recipe, label=None,
                 jtype='docker', cpus=None, memory_limit=None,
                 singularity_dir=None,
                 time_out=-1,
                 logger=None,
                 logfile=None,
                 cabpath=None):
        """

        logger:   if set to a logger object, uses the specified logger.
                  if None, sets up its own logger using the parameters below

        logfile:  name of logfile, False to disable recipe-level logfiles, or None to form a default name
        """
        self.name = name
        self.recipe = recipe
        self.label = label or '{0}({1})'.format(name, id(name))
        self.log = recipe.log
        self.active = False
        self.jtype = jtype  # ['docker', 'python', singularity', 'udocker']
        self.job = None
        self.created = False
        self.args = ['--user {}:{}'.format(UID, GID)]
        if cpus:
            self.args.append("--cpus {0:f}".format(cpus))
        if memory_limit:
            self.args.append("--memory {0:s}".format(memory_limit))
        self.time_out = time_out

        self.logfile = logfile
        if self.logfile is not False:
            self.logfile = logfile or "log-{0:s}.txt".format(self.name)

        self.cabpath = cabpath

    def setup_job_log(self, log_name=None):
        """ set up a log for the job on the host side 
            log_name: preferably unique name for this jobs log
            log_dir: log base directory, None is current directory
        """
        log_name = log_name or self.name
        if log_name not in StimelaJob.logs_avail:
            self.log = stimela.logger().getChild(log_name)

            if self.logfile is not False:
                log_dir = os.path.dirname(self.logfile) or "."
                if not os.path.exists(log_dir):
                    os.mkdir(log_dir)
                fh = logging.FileHandler(self.logfile, 'w', delay=True)
                fh.setLevel(logging.INFO)
                self.log.addHandler(fh)

            self.log.propagate = True            # propagate also to main stimela logger

            StimelaJob.logs_avail[log_name] = self.log
        else:
            self.log = StimelaJob.logs_avail[log_name]



    def setup_job(self, image, config,
                   indir=None, outdir=None, msdir=None, 
                   build_label=None, singularity_image_dir=None,
                   **kw):
        """
            Setup job

        image   :   stimela cab name, e.g. 'cab/simms'
        name    :   This name will be part of the name of the contaier that will 
                    execute the task (now optional)
        config  :   Dictionary of options to parse to the task. This will modify 
                    the parameters in the default parameter file which 
                    can be viewd by running 'stimela cabs -i <cab name>', e.g 'stimela cabs -i simms'
        indir   :   input dirctory for cab
        outdir  :   output directory for cab
        msdir   :   MS directory for cab. Only specify if different from recipe ms_dir

        function    :   Python callable to execute
        name        :   Name of function (if not given, will used function.__name__)
        parameters  :   Parameters to parse to function
        label       :   Function label; for logging purposes
        """
        
        if self.jtype == "python":
            self.image = image.__name__
            if not callable(image):
                raise utils.StimelaCabRuntimeError(
                    'Object given as function is not callable')

            if self.name is None:
                self.name = image.__name__

            self.job = {
                'function':   image,
                'parameters':   config,
            }

            return 0

        # check if name has any offending characters
        offenders = re.findall('[^\w .-]', self.name)
        if offenders:
            raise StimelaCabParameterError('The cab name \'{:s}\' contains invalid characters.'
                                           ' Allowed charcaters are alphanumeric, plus [-_. ].'.format(self.name))

        # Update I/O with values specified on command line
        script_context = self.recipe.stimela_context
        indir = script_context.get('_STIMELA_INPUT', None) or indir
        outdir = script_context.get('_STIMELA_OUTPUT', None) or outdir
        msdir = script_context.get('_STIMELA_MSDIR', None) or msdir
        build_label = script_context.get(
            '_STIMELA_BUILD_LABEL', None) or build_label

        self.setup_job_log()

        # make name palatable as container name
        pausterized_name = re.sub("[\W]", "_", self.name)

        name = '{0}-{1}{2}'.format(pausterized_name, id(image),
                                   str(time.time()).replace('.', ''))

        cont = getattr(CONT_MOD[self.jtype], "Container")(image, name,
                                     logger=self.log, 
                                     workdir=WORKDIR,
                                     time_out=self.time_out)
        if self.jtype == "docker":
            # Get location of template parameters file
            cabs_loc = f"{stimela.LOG_HOME}/{build_label}_stimela_logfile.json"
            cabs_logger = get_cabs(cabs_loc)
            try:
                cabpath = cabs_logger[f'{build_label}_{cont.image}']['DIR']
            except KeyError:
                main.build(["--us-only", cont.image.split("/")[-1],
                        "--no-cache", "--build-label", build_label])
                cabs_logger = get_cabs(cabs_loc)
                cabpath = cabs_logger[f'{build_label}_{cont.image}']['DIR']

        else:
            cabpath = os.path.join(CAB_PATH, image.split("/")[1])
        
        # In case the user specified a custom cab
        cabpath = os.path.join(self.cabpath, image.split("/")[1]) if self.cabpath else cabpath
        parameter_file = os.path.join(cabpath, 'parameters.json')
        _cab = cab.CabDefinition(indir=indir, outdir=outdir,
                                 msdir=msdir, parameter_file=parameter_file)
        cont.IODEST = CONT_IO
        cont.cabname = _cab.task

        if self.jtype == "docker":
            cont.image = '{0}_{1}'.format(build_label, image)
        elif self.jtype == "singularity":
            simage = _cab.base.replace("/", "_")
            if singularity_image_dir is None:
                singularity_image_dir = os.path.join(".", "stimela_singularity_images")
            cont.image = '{0:s}/{1:s}_{2:s}{3:s}'.format(singularity_image_dir,
                    simage, _cab.tag, singularity.suffix)
            if not os.path.exists(cont.image):
                main.pull(f"-s -cb {cont.cabname} -pf {singularity_image_dir}".split())
        else:
            cont.image = ":".join([_cab.base, _cab.tag])

        # Container parameter file will be updated and validated before the container is executed
        cont._cab = _cab
        cont.parameter_file_name = '{0}/{1}.json'.format(
            self.recipe.parameter_file_dir, name)

        self.image = str(cont.image)

        # Remove dismissable kw arguments:
        ops_to_pop = []
        for op in config:
            if isinstance(config[op], dismissable):
                ops_to_pop.append(op)
        for op in ops_to_pop:
            arg = config.pop(op)()
            if arg is not None:
                config[op] = arg
        cont.config = config

        # These are standard volumes and
        # environmental variables. These will be
        # always exist in a cab container
        cont.add_volume(self.recipe.stimela_path,
                        '/scratch/stimela', perm='ro')
        cont.add_volume(cont.parameter_file_name,
                        '/scratch/configfile', perm='ro', noverify=True)
        cont.add_volume(os.path.join(cabpath, "src"), "/scratch/code", "ro")



        if self.jtype == "singularity":
            cont.RUNSCRIPT = f"/{self.jtype}"
        else:
            cont.RUNSCRIPT = f"/{self.jtype}_run"

        cont.add_volume(f"{BIN}/stimela_runscript", 
                cont.RUNSCRIPT, perm="ro")

        cont.add_environ('CONFIG', '/scratch/configfile')
        cont.add_environ('HOME', WORKDIR)

        if msdir:
            md = cont.IODEST["msfile"]
            cont.add_volume(msdir, md)
            cont.add_environ("MSDIR", md)
            # Keep a record of the content of the
            # volume
            dirname, dirs, files = [a for a in next(os.walk(msdir))]
            cont.msdir_content = {
                "volume":   dirname,
                "dirs":   dirs,
                "files":   files,
            }

            self.log.debug(
                'Mounting volume \'{0}\' from local file system to \'{1}\' in the container'.format(msdir, md))

        if indir:
            cont.add_volume(indir, cont.IODEST["input"], perm='ro')
            cont.add_environ("INPUT", cont.IODEST["input"])
            # Keep a record of the content of the
            # volume
            dirname, dirs, files = [a for a in next(os.walk(indir))]
            cont.input_content = {
                "volume":   dirname,
                "dirs":   dirs,
                "files":   files,
            }

            self.log.debug('Mounting volume \'{0}\' from local file system to \'{1}\' in the container'.format(
                indir, cont.IODEST["input"]))

        if not os.path.exists(outdir):
            os.mkdir(outdir)

        od = cont.IODEST["output"]

        cont.logfile = self.logfile
        cont.add_volume(outdir, od, "rw")
        cont.add_environ("OUTPUT", od)

        # temp files go into output
        tmpfol = os.path.join(outdir, "tmp")
        if not os.path.exists(tmpfol):
            os.mkdir(tmpfol)
        cont.add_volume(tmpfol, cont.IODEST["tmp"], "rw")
        cont.add_environ("TMPDIR", cont.IODEST["tmp"])

        self.log.debug(
            'Mounting volume \'{0}\' from local file system to \'{1}\' in the container'.format(outdir, od))

        # Added and ready for execution
        self.job = cont

        return 0

    def run_job(self):

        if isinstance(self.job, dict):
            function = self.job['function']
            options = self.job['parameters']
            function(**options)
            return 0

        if hasattr(self.job, '_cab'):
            self.job._cab.update(self.job.config,
                                 self.job.parameter_file_name)

        if self.jtype == "singularity":
            self.created = True
            self.job.run()
            return 0
        else:
            self.created = False
            self.job.create(*self.args)
            self.created = True
            self.job.start()
            return 0


class Recipe(object):
    def __init__(self, name, data=None,
                 parameter_file_dir=None, ms_dir=None,
                 tag=None, build_label=None,
                 singularity_image_dir=None, JOB_TYPE='docker',
                 cabpath=None,
                 logger=None,
                 log_dir=None, logfile=None, logfile_task=None):
        """
        Deifine and manage a stimela recipe instance.        

        name    :   Name of stimela recipe
        msdir   :   Path of MSs to be used during the execution of the recipe
        tag     :   Use cabs with a specific tag
        parameter_file_dir :   Will store task specific parameter files here

        logger:   if set to a logger object, uses the specified logger.
                  if None, sets up its own logger using the parameters below

        loglevel: default logging level
        log_dir:  default directory for logfiles
        logfile:  name of logfile, False to disable recipe-level logfiles, or None to form a default name

        logfile_task: name of task-level logfile, False to disable task-level logfiles, or None to form a default name.
                      logfile_task may contain a "{task}" entry which will be substituted for a task name.
        """
        self.name = name
        self.name_ = re.sub(r'\W', '_', name)  # pausterized name

        self.cabpath = cabpath

        # set default name for task-level logfiles
        self.logfile_task = "{0}/log-{1}-{{task}}".format(log_dir or ".", self.name) \
            if logfile_task is None else logfile_task

        if logger is not None:
            self.log = logger
        else:
            self.log = stimela.logger().getChild(name)
            self.log.propagate = True # propagate to main stimela logger

            # logfile is False: no logfile at recipe level
            if logfile is not False:
                # logfile is None: use default name
                if logfile is None:
                    logfile = "{0}/log-{1}.txt".format(log_dir or ".", self.name)

                # reset default name for task-level logfiles based on logfile
                self.logfile_task = os.path.splitext(logfile)[0] + "-{task}.txt" \
                            if logfile_task is None else logfile_task

                # ensure directory exists
                log_dir = os.path.dirname(logfile) or "."
                if not os.path.exists(log_dir):
                    self.log.info('creating log directory {0:s}'.format(log_dir))
                    os.makedirs(log_dir)

                fh = logging.FileHandler(logfile, 'w', delay=True)
                fh.setLevel(logging.INFO)
                fh.setFormatter(stimela.log_formatter)
                self.log.addHandler(fh)

        self.JOB_TYPE = JOB_TYPE

        self.resume_file = '.last_{}.json'.format(self.name_)
        self.stimela_context = inspect.currentframe().f_back.f_globals
        self.stimela_path = os.path.dirname(docker.__file__)

        self.build_label = build_label or stimela.CAB_USERNAME
        self.ms_dir = ms_dir
        if not os.path.exists(self.ms_dir):
            self.log.info(
                'MS directory \'{}\' does not exist. Will create it'.format(self.ms_dir))
            os.mkdir(self.ms_dir)
        self.tag = tag
        # create a folder to store config files
        # if it doesn't exist. These config
        # files can be resued to re-run the
        # task
        self.parameter_file_dir = parameter_file_dir or "stimela_parameter_files"
        if not os.path.exists(self.parameter_file_dir):
            self.log.info(
                'Config directory cannot be found. Will create ./{}'.format(self.parameter_file_dir))
            os.mkdir(self.parameter_file_dir)

        self.jobs = []
        self.completed = []
        self.failed = None
        self.remaining = []

        self.pid = os.getpid()
        self.singularity_image_dir = singularity_image_dir
        if self.singularity_image_dir and not self.JOB_TYPE:
            self.JOB_TYPE = "singularity"

        self.log.info('---------------------------------')
        self.log.info('Stimela version {0}'.format(stimela.__version__))
        self.log.info('Sphesihle Makhathini <sphemakh@gmail.com>')
        self.log.info('Running: {:s}'.format(self.name))
        self.log.info('---------------------------------')

    def add(self, image, name, config=None,
            input=None, output=None, msdir=None,
            label=None, shared_memory='1gb',
            build_label=None,
            cpus=None, memory_limit=None,
            time_out=-1,
            logger=None,
            logfile=None,
            cabpath=None):

        if not os.path.exists(output):
            self.log.info(
                    'The Log directory \'{0:s}\' cannot be found. Will create it'.format(output))
            os.mkdir(output)

        if logfile is None:
            logfile = False if self.logfile_task is False else self.logfile_task.format(task=name)

        job = StimelaJob(name, recipe=self, label=label,
                         cpus=cpus, memory_limit=memory_limit, time_out=time_out,
                         jtype=self.JOB_TYPE,
                         logger=logger, logfile=logfile,
                         cabpath=cabpath or self.cabpath)

        if callable(image):
            job.jtype = 'python'
        
        job.setup_job(image=image, config=config,
                 indir=input, outdir=output, msdir=msdir or self.ms_dir,
                 shared_memory=shared_memory, build_label=build_label or self.build_label,
                 singularity_image_dir=self.singularity_image_dir,
                 time_out=time_out)

        self.log.info('Adding cab \'{0}\' to recipe. The container will be named \'{1}\''.format(
            job.image, name))
        self.jobs.append(job)

        return 0

    def log2recipe(self, job, recipe, num, status):

        if job.jtype in ['docker', 'singularity', 'udocker', 'podman']:
            cont = job.job
            step = {
                "name":   cont.name,
                "number":   num,
                "cab":   cont.image,
                "volumes":   cont.volumes,
                "environs":   getattr(cont, "environs", None),
                "shared_memory":   getattr(cont, "shared_memory", None),
                "input_content":   cont.input_content,
                "msdir_content":   cont.msdir_content,
                "label":   getattr(cont, "label", ""),
                "logfile":   cont.logfile,
                "status":   status,
                "jtype":   job.jtype,
            }
        else:
            step = {
                "name":   job.name,
                "number":   num,
                "label":   job.label,
                "status":   status,
                "function":   job.job['function'].__name__,
                "jtype":   'function',
                "parameters":   job.job['parameters'],
            }

        recipe['steps'].append(step)

        return 0

    def run(self, steps=None, resume=False, redo=None):
        """
        Run a Stimela recipe. 

        steps   :   recipe steps to run
        resume  :   resume recipe from last run
        redo    :   Re-run an old recipe from a .last file
        """

        recipe = {
            "name":   self.name,
            "steps":   []
        }
        start_at = 0

        if redo:
            recipe = utils.readJson(redo)
            self.log.info('Rerunning recipe {0} from {1}'.format(
                recipe['name'], redo))
            self.log.info('Recreating recipe instance..')
            self.jobs = []
            for step in recipe['steps']:

                #        add I/O folders to the json file
                #        add a string describing the contents of these folders
                #        The user has to ensure that these folders exist, and have the required content
                if step['jtype'] == 'docker':
                    self.log.info('Adding job \'{0}\' to recipe. The container will be named \'{1}\''.format(
                        step['cab'], step['name']))
                    cont = docker.Container(step['cab'], step['name'],
                                            label=step['label'], logger=self.log,
                                            shared_memory=step['shared_memory'],
                                            workdir=WORKDIR)

                    self.log.debug('Adding volumes {0} and environmental variables {1}'.format(
                        step['volumes'], step['environs']))
                    cont.volumes = step['volumes']
                    cont.environs = step['environs']
                    cont.shared_memory = step['shared_memory']
                    cont.input_content = step['input_content']
                    cont.msdir_content = step['msdir_content']
                    cont.logfile = step['logfile']
                    job = StimelaJob(
                        step['name'], recipe=self, label=step['label'], cabpath=self.cabpath)
                    job.job = cont
                    job.jtype = 'docker'
                elif step['jtype'] == 'function':
                    name = step['name']
                    func = inspect.currentframe(
                    ).f_back.f_locals[step['function']]
                    job = StimelaJob(name, recipe=self, label=step['label'])
                    job.python_job(func, step['parameters'])
                    job.jtype = 'function'

                self.jobs.append(job)

        elif resume:
            self.log.info("Resuming recipe from last run.")
            try:
                recipe = utils.readJson(self.resume_file)
            except IOError:
                raise StimelaRecipeExecutionError(
                    "Cannot resume pipeline, resume file '{}' not found".format(self.resume_file))

            steps_ = recipe.pop('steps')
            recipe['steps'] = []
            _steps = []
            for step in steps_:
                if step['status'] == 'completed':
                    recipe['steps'].append(step)
                    continue

                label = step['label']
                number = step['number']

                # Check if the recipe flow has changed
                if label == self.jobs[number-1].label:
                    self.log.info(
                        'recipe step \'{0}\' is fit for re-execution. Label = {1}'.format(number, label))
                    _steps.append(number)
                else:
                    raise StimelaRecipeExecutionError(
                        'Recipe flow, or task scheduling has changed. Cannot resume recipe. Label = {0}'.format(label))

            # Check whether there are steps to resume
            if len(_steps) == 0:
                self.log.info(
                    'All the steps were completed. No steps to resume')
                sys.exit(0)
            steps = _steps

        if getattr(steps, '__iter__', False):
            _steps = []
            if isinstance(steps[0], str):
                labels = [job.label.split('::')[0] for job in self.jobs]

                for step in steps:
                    try:
                        _steps.append(labels.index(step)+1)
                    except ValueError:
                        raise StimelaCabParameterError(
                            'Recipe label ID [{0}] doesn\'t exist'.format(step))
                steps = _steps
        else:
            steps = range(1, len(self.jobs)+1)
        jobs = [(step, self.jobs[step-1]) for step in steps]

        # TIMESTR = "%Y-%m-%d %H:%M:%S"
        # TIMESTR = "%H:%M:%S"

        for i, (step, job) in enumerate(jobs):
            start_time = datetime.now()
            job.log.info('job started at {}'.format(start_time),
                          # the extra attributes are filtered by e.g. the CARACal logger
                          extra=dict(stimela_job_state=(job.name, "running")))

            self.log.info('STEP {0} :: {1}'.format(i+1, job.label))
            self.active = job
            try:
                with open(job.logfile, 'a') as astd:
                    astd.write('\n-----------------------------------\n')
                    astd.write(
                        'Stimela version     : {}\n'.format(version))
                    astd.write(
                        'Cab name            : {}\n'.format(job.image))
                    astd.write('-------------------------------------\n')
                job.run_job()

                self.log2recipe(job, recipe, step, 'completed')
                self.completed.append(job)

                finished_time = datetime.now()
                job.log.info('job complete at {} after {}'.format(finished_time, finished_time-start_time),
                              # the extra attributes are filtered by e.g. the CARACal logger
                              extra=dict(stimela_job_state=(job.name, "complete")))

            except (utils.StimelaCabRuntimeError,
                    StimelaRecipeExecutionError,
                    StimelaCabParameterError) as e:
                self.remaining = [jb[1] for jb in jobs[i+1:]]
                self.failed = job

                finished_time = datetime.now()
                job.log.error(str(e), extra=dict(stimela_job_state=(job.name, "failed"), boldface=True))
                job.log.error('job failed at {} after {}'.format(finished_time, finished_time-start_time),
                                extra=dict(stimela_job_state=(job.name, "failed"), color=None))
                for line in traceback.format_exc().splitlines():
                    job.log.error(line, extra=dict(traceback_report=True))

                self.log.info('Completed jobs : {}'.format(
                    [c.name for c in self.completed]))
                self.log.info('Remaining jobs : {}'.format(
                    [c.name for c in self.remaining]))

                self.log2recipe(job, recipe, step, 'failed')
                for step, jb in jobs[i+1:]:
                    self.log.info(
                        'Logging remaining task: {}'.format(jb.label))
                    self.log2recipe(jb, recipe, step, 'remaining')

                self.log.info(
                    'Saving pipeline information in {}'.format(self.resume_file))
                utils.writeJson(self.resume_file, recipe)

                # raise pipeline exception. Original exception context is discarded by "from None" (since we've already
                # logged it above, we don't need to include it with the new exception)
                raise PipelineException(e, self.completed, job, self.remaining) from None

        self.log.info(
            'Saving pipeline information in {}'.format(self.resume_file))
        utils.writeJson(self.resume_file, recipe)
        self.log.info('Recipe executed successfully')

        return 0
