# -*- coding: future_fstrings -*-
import os
import sys
import pwd, grp
import time
import stimela
from stimela import docker, singularity, utils, cargo, podman, main
from stimela.cargo import cab
import logging
import inspect
import re
from stimela.exceptions import *
from stimela.dismissable import dismissable
from stimela.cargo.cab import StimelaCabParameterError
from datetime import datetime
import traceback
import shutil
import re

version = stimela.__version__
UID = os.getuid()
GID = os.getgid()
CAB_PATH = os.path.abspath(os.path.dirname(cab.__file__))

CONT_MOD = {
        "docker" : docker,
        "singularity" : singularity,
        "podman" : podman
        }

CONT_IO = cab.IODEST
CDIR = os.getcwd()

PULLFOLDER = os.environ.get("STIMELA_PULLFOLDER", CDIR)

# make dictionary of wrangler actions. First, add all logging levels
_actions = {attr: value for attr, value in logging.__dict__.items() if attr.upper() == attr and type(value) is int}

# then add constants for other wrangler actions
_SUPPRESS = _actions["SUPPRESS"] = "SUPPRESS"
_DECLARE_SUCCESS = _actions["DECLARE_SUCCESS"] = "DECLARE_SUPPRESS"
_DECLARE_FAILURE = _actions["DECLARE_FAILURE"] = "DECLARE_FAILURE"


class StimelaJob(object):
    logs_avail = dict()
    def __init__(self, name, recipe, label=None,
                 jtype='docker', cpus=None, memory_limit=None,
                 singularity_dir=None,
                 time_out=-1,
                 logger=None,
                 logfile=None,
                 cabpath=None,
                 workdir=None,
                 tag=None,
                 version=None,
                 force_tag=False,
                 shared_memory=None):
        """

        logger:   if set to a logger object, uses the specified logger.
                  if None, sets up its own logger using the parameters below

        logfile:  name of logfile, False to disable recipe-level logfiles, or None to form a default name
        """
        self.tag = tag
        self.version = version
        self.force_tag = force_tag
        self.name = name
        self.recipe = recipe
        self.label = label or '{0}({1})'.format(name, id(name))
        self.log = recipe.log
        self._log_fh = None
        self.active = False
        self.jtype = jtype  # ['docker', 'python', singularity']
        self.job = None
        self.created = False
        self.wranglers = []
        self.args = ['--user {}:{}'.format(UID, GID)]
        if cpus:
            self.args.append("--cpus {0:f}".format(cpus))
        if memory_limit:
            self.args.append("--memory {0:s}".format(memory_limit))
        if shared_memory:
            self.args.append("--shm-size {0:s}".format(shared_memory))
        self.time_out = time_out

        self.logfile = logfile
        if self.logfile is not False:
            self.logfile = logfile or "log-{0:s}.txt".format(self.name)

        self.cabpath = cabpath
        self.workdir = workdir

    def setup_job_log(self, log_name=None, loglevel=None):
        """ set up a log for the job on the host side 
            log_name: preferably unique name for this jobs log
            log_dir: log base directory, None is current directory
        """
        loglevel = loglevel or self.recipe.loglevel
        log_name = log_name or self.name
        if log_name not in StimelaJob.logs_avail:
            self.log = stimela.logger().getChild(log_name)

            if self.logfile is not False:
                log_dir = os.path.dirname(self.logfile) or "."
                if not os.path.exists(log_dir):
                    os.mkdir(log_dir)
                self._log_fh = logging.FileHandler(self.logfile, 'w', delay=True)
                self._log_fh.setLevel(getattr(logging, loglevel))
                self.log.addHandler(self._log_fh)

            self.log.propagate = True            # propagate also to main stimela logger

            StimelaJob.logs_avail[log_name] = self.log
        else:
            self.log = StimelaJob.logs_avail[log_name]

    def setup_output_wranglers(self, wranglers):
        self._wranglers = []
        if not wranglers:
            return
        if type(wranglers) is not dict:
            raise utils.StimelaCabRuntimeError("wranglers: dict expected")
        for match, actions in wranglers.items():
            replace = None
            if type(actions) is str:
                actions = [actions]
            if type(actions) is not list:
                raise utils.StimelaCabRuntimeError(f"wrangler entry {match}: expected action or list of action")
            for action in actions:
                if action.startswith("replace:"):
                    replace = action.split(":", 1)[1]
                elif action not in _actions:
                    raise utils.StimelaCabRuntimeError(f"wrangler entry {match}: unknown action '{action}'")
            actions = [_actions[act] for act in actions if act in _actions]
            self._wranglers.append((re.compile(match), replace, actions))

    def apply_output_wranglers(self, output, severity, logger):
        suppress = False
        modified_output = output
        for regex, replace, actions in self._wranglers:
            if regex.search(output):
                if replace is not None:
                    modified_output = regex.sub(replace, output)
                for action in actions:
                    if type(action) is int:
                        severity = action
                    elif action is _SUPPRESS:
                        suppress = True
                    elif action is _DECLARE_FAILURE and self.declare_status is None:
                        self.declare_status = False
                        modified_output = "[FAILURE] " + modified_output
                        severity = logging.ERROR
                    elif action is _DECLARE_SUCCESS and self.declare_status is None:
                        self.declare_status = True
                        modified_output = "[SUCCESS] " + modified_output
        return (None, 0) if suppress else (modified_output, severity)

    def setup_job(self, image, config,
                   indir=None, outdir=None, msdir=None, 
                   singularity_image_dir=None, repository=None):
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
            self.setup_job_log()

            return 0

        # check if name has any offending characters
        offenders = re.findall('[^\w .-]', self.name)
        if offenders:
            raise StimelaCabParameterError('The cab name \'{:s}\' contains invalid characters.'
                                           ' Allowed charcaters are alphanumeric, plus [-_. ].'.format(self.name))

        self.setup_job_log()

        # make name palatable as container name
        pausterized_name = re.sub("[\W]", "_", self.name)

        name = '{0}-{1}{2}'.format(pausterized_name, id(image),
                                   str(time.time()).replace('.', ''))

        cont = getattr(CONT_MOD[self.jtype], "Container")(image, name,
                                     logger=self.log, 
                                     workdir=CONT_IO["output"],
                                     time_out=self.time_out)

        cabpath = os.path.join(CAB_PATH, image.split("/")[1])
        
        # In case the user specified a custom cab
        cabpath = os.path.join(self.cabpath, image.split("/")[1]) if self.cabpath else cabpath
        parameter_file = os.path.join(cabpath, 'parameters.json')
        _cab = cab.CabDefinition(indir=indir, outdir=outdir,
                                 msdir=msdir, parameter_file=parameter_file)
        param = utils.readJson(parameter_file)
        _repository = param.get("hub", repository)
        self.setup_output_wranglers(_cab.wranglers)
        cont.IODEST = CONT_IO
        cont.cabname = _cab.task

#
#Example
#        ----------------
# casa_listobs:
#   tag: <tag>               ## optional
#   version: <version>       ## optional. If version is a dict, then ignore tag and priority and use <tag>:<version> pairs in dict
#   force: true              ## Continue even if tag is specified in the parameters.json file

        no_tag_version = False
        if self.tag or self.version:
            tvi = None
            if self.tag:
                try:
                    tvi = _cab.tag.index(self.tag)
                except ValueError:
                    pass
            elif self.version:
                try:
                    tvi = _cab.version.index(self.version)
                except ValueError:
                    self.log.error(f"The version, {self.version}, specified for cab '{_cab.task}' is unknown. Available versions are {_cab.version}")
                    raise ValueError 
            if tvi is None:
                tvi = -1
            self.tag = _cab.tag[tvi]
            self.version = _cab.version[tvi]
        else:
            self.tag = _cab.tag[-1]
            self.version = _cab.version[-1]

        cabspecs = self.recipe.cabspecs.get(cont.cabname, None)
        if cabspecs:
            _tag = cabspecs.get("tag", None)
            _version = cabspecs.get("version", None)
            _force_tag = cabspecs.get("force", False)
            if isinstance(_version, dict):
                if self.version in _version:
                    self.tag = _version[self.version]
            elif _version:
                self.version = _version
            else:
                self.tag = _tag
            if self.version and self.version not in _cab.version:
                self.log.error(f"The version, {self.version}, specified for cab '{_cab.task}' is unknown. Available versions are {_cab.version}")
                raise ValueError
            if not _tag:
                idx = _cab.version.index(self.version)
                self.tag = _cab.tag[idx]
            self.force_tag = _force_tag

        if self.tag not in _cab.tag:
            if self.force_tag:
                self.log.warn(f"You have chosen to use an unverified base image '{_cab.base}:{self.tag}'. May the force be with you.")
            else:
                raise StimelaBaseImageError(f"The base image '{_cab.base}' with tag '{self.tag}' has not been verified. If you wish to continue with it, please add the 'force_tag' when adding it to your recipe")
        if _repository:
            image_url = f"{_repository}/{_cab.base}:{self.tag}" if _repository != "docker" and _repository != "docker.io" else \
                        f"{_cab.base}:{self.tag}"
        else:
            image_url = f"{_cab.base}:{self.tag}"

        if self.jtype == "singularity":
            simage = _cab.base.replace("/", "_")
            cont.image = '{0:s}/{1:s}_{2:s}{3:s}'.format(singularity_image_dir,
                    simage, self.tag, singularity.suffix)
            cont.image = os.path.abspath(cont.image)
            if not os.path.exists(cont.image):
                singularity.pull(image_url, 
                        os.path.basename(cont.image), directory=singularity_image_dir)
        else:
            cont.image = image_url

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
        cont.add_volume(cont.parameter_file_name,
                        f'{cab.MOUNT}/configfile', perm='ro', noverify=True)
        cont.add_volume(os.path.join(cabpath, "src"), f"{cab.MOUNT}/code", "ro")

        cont.add_volume(os.path.join(self.workdir, "passwd"), "/etc/passwd")
        cont.add_volume(os.path.join(self.workdir, "group"), "/etc/group")
        cont.RUNSCRIPT = f"/{self.jtype}_run"

        if self.jtype == "singularity":
            cont.RUNSCRIPT = f"/{self.jtype}"
            if _cab.base.startswith("stimela/casa") or _cab.base.startswith("stimela/simms"):
                cont.add_environ("LANGUAGE", "en_US.UTF-8")
                cont.add_environ("LANG", "en_US.UTF-8")
                cont.add_environ("LC_ALL", "en_US.UTF-8")
            cont.execdir = self.workdir
        else:
            cont.RUNSCRIPT = f"/{self.jtype}_run"
        
        runscript = shutil.which("stimela_runscript")
        if runscript:
            cont.add_volume(runscript, 
                    cont.RUNSCRIPT, perm="ro")
        else:
            self.log.error("Stimela container runscript could not found.\
                    This may due to conflicting python or stimela installations in your $PATH.")
            raise OSError

        cont.add_environ('CONFIG', f'{cab.MOUNT}/configfile')
        cont.add_environ('HOME', cont.IODEST["output"])
        cont.add_environ('STIMELA_MOUNT', cab.MOUNT)

        if msdir:
            md = cont.IODEST["msfile"]
            os.makedirs(msdir, exist_ok=True)
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

        os.makedirs(outdir, exist_ok=True)

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
        self.declare_status = None

        if isinstance(self.job, dict):
            function = self.job['function']
            options = self.job['parameters']
            function(**options)
            return 0

        if hasattr(self.job, '_cab'):
            self.job._cab.update(self.job.config,
                                 self.job.parameter_file_name, tag=self.tag)

        if self.jtype == "singularity":
            self.created = True
            self.job.run(output_wrangler=self.apply_output_wranglers)
        elif self.jtype in ["podman", "docker"]:
            self.created = False
            self.job.create(*self.args)
            self.created = True
            self.job.start(output_wrangler=self.apply_output_wranglers)
        return 0

    def close(self):
        """Call this to explicitly clean up after the job"""
        if self._log_fh is not None:
            self._log_fh.close()

    def __del__(self):
        self.close()


class Recipe(object):
    def __init__(self, name, data=None,
                 parameter_file_dir=None, ms_dir=None,
                 build_label=None,
                 singularity_image_dir=None, JOB_TYPE='docker',
                 cabpath=None,
                 logger=None,
                 msdir=None,
                 indir=None,
                 outdir=None,
                 log_dir=None, logfile=None, logfile_task=None,
                 cabspecs=None,
                 repository="quay.io",
                 loglevel="INFO"):
        """
        Deifine and manage a stimela recipe instance.        

        name    :   Name of stimela recipe
        msdir   :   Path of MSs to be used during the execution of the recipe
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
        self.repository = repository
        self.name_ = re.sub(r'\W', '_', name)  # pausterized name

        self.stimela_context = inspect.currentframe().f_back.f_globals
        self.stimela_path = os.path.dirname(docker.__file__)
        # Update I/O with values specified on command line
        self.indir = indir
        self.outdir = outdir
        self.msdir = self.ms_dir = msdir or ms_dir
        self.loglevel = self.stimela_context.get('_STIMELA_LOG_LEVEL', None) or loglevel
        self.JOB_TYPE = self.stimela_context.get('_STIMELA_JOB_TYPE', None) or JOB_TYPE

        self.cabpath = cabpath
        self.cabspecs = cabspecs or {}

        # set default name for task-level logfiles
        self.logfile_task = "{0}/log-{1}-{{task}}".format(log_dir or ".", self.name_) \
            if logfile_task is None else logfile_task

        self._log_fh = None

        if logger is not None:
            self.log = logger
        else:
            logger = stimela.logger(loglevel=self.loglevel)
            self.log = logger.getChild(name)
            self.log.propagate = True # propagate to main stimela logger

            # logfile is False: no logfile at recipe level
            if logfile is not False:
                # logfile is None: use default name
                if logfile is None:
                    logfile = "{0}/log-{1}.txt".format(log_dir or ".", self.name_)

                # reset default name for task-level logfiles based on logfile
                self.logfile_task = os.path.splitext(logfile)[0] + "-{task}.txt" \
                            if logfile_task is None else logfile_task

                # ensure directory exists
                log_dir = os.path.dirname(logfile) or "."
                if not os.path.exists(log_dir):
                    self.log.info('creating log directory {0:s}'.format(log_dir))
                    os.makedirs(log_dir)

                self._log_fh = logging.FileHandler(logfile, 'w', delay=True)
                self._log_fh.setLevel(getattr(logging, self.loglevel))
                self._log_fh.setFormatter(stimela.log_formatter)
                self.log.addHandler(self._log_fh)

        self.resume_file = '.last_{}.json'.format(self.name_)
        # set to default if not set
        # create a folder to store config files
        # if it doesn't exist. These config
        # files can be resued to re-run the
        # task

        self.jobs = []
        self.completed = []
        self.failed = None
        self.remaining = []

        self.pid = os.getpid()

        cmd_line_pf = self.stimela_context.get('_STIMELA_PULLFOLDER', None)
        self.singularity_image_dir = cmd_line_pf or singularity_image_dir or PULLFOLDER
        if self.singularity_image_dir and not self.JOB_TYPE:
            self.JOB_TYPE = "singularity"

        self.log.info('---------------------------------')
        self.log.info('Stimela version {0}'.format(stimela.__version__))
        self.log.info('Running: {:s}'.format(self.name))
        self.log.info('---------------------------------')
        
        self.workdir = None
        self.__make_workdir()

        self.parameter_file_dir = parameter_file_dir or f'{self.workdir}/stimela_parameter_files'
        if not os.path.exists(self.parameter_file_dir):
            self.log.info(
                f'Config directory cannot be found. Will create {self.parameter_file_dir}')
            os.mkdir(self.parameter_file_dir)

    def __make_workdir(self):
        timestamp = str(time.time()).replace(".", "")
        self.workdir = os.path.join(CDIR, f".stimela_workdir-{timestamp}")
        while os.path.exists(self.workdir):
            timestamp = str(time.time()).replace(".", "")
            self.workdir = os.path.join(CDIR, f".stimela_workdir-{timestamp}")
        os.mkdir(self.workdir)
        # create passwd and group files to be mounted inside the container
        template_dir = os.path.join(os.path.dirname(__file__), "cargo/base")
        # get current user info
        pw = pwd.getpwuid(os.getuid())
        gr = grp.getgrgid(pw.pw_gid)
        with open(os.path.join(self.workdir, "passwd"), "wt") as file:
            file.write(open(os.path.join(template_dir, "passwd.template"), "rt").read())
            file.write(f"{pw.pw_name}:x:{pw.pw_uid}:{pw.pw_gid}:{pw.pw_gecos}:/:/bin/bash")
        with open(os.path.join(self.workdir, "group"), "wt") as file:
            file.write(open(os.path.join(template_dir, "group.template"), "rt").read())
            file.write(f"{gr.gr_name}:x:{gr.gr_gid}:")


    def add(self, image, name, config=None,
            input=None, output=None, msdir=None,
            label=None, shared_memory='1gb',
            build_label=None,
            cpus=None, memory_limit=None,
            time_out=-1,
            logger=None,
            logfile=None,
            cabpath=None,
            tag=None,
            version=None,
            force_tag=False):

        if logfile is None:
            logfile = False if self.logfile_task is False else self.logfile_task.format(task=name)

        job = StimelaJob(name, recipe=self, label=label,
                         cpus=cpus, memory_limit=memory_limit,
                         shared_memory=shared_memory,
                         time_out=time_out,
                         jtype=self.JOB_TYPE,
                         logger=logger, logfile=logfile,
                         cabpath=cabpath or self.cabpath,
                         workdir=self.workdir, tag=tag, version=version, force_tag=force_tag)

        if callable(image):
            job.jtype = 'python'
        
        _indir = self.stimela_context.get('_STIMELA_INPUT', None) or input
        _outdir = self.stimela_context.get('_STIMELA_OUTPUT', None) or  output
        _msdir = self.stimela_context.get('_STIMELA_MSDIR', None) or msdir
        # The hirechy is command line, Recipe.add, and then Recipe
        indir = _indir or self.indir
        outdir = _outdir or self.outdir
        msdir = _msdir or self.msdir

        job.setup_job(image=image, config=config,
             indir=indir, outdir=outdir, msdir=msdir,
             singularity_image_dir=self.singularity_image_dir, 
             repository=self.repository)

        self.log.info(f'Adding cab \'{job.image}\' ({job.version}) to recipe, container name \'{name}\'')
        self.jobs.append(job)

        return 0

    def log2recipe(self, job, recipe, num, status):

        if job.jtype in ['docker', 'singularity', 'podman']:
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
            self.log.error("This feature has been depricated")
            raise SystemExit

        elif resume:
            #TODO(sphe) Need to re-think how best to do this
            self.log.error("This feature has been depricated")
            raise SystemExit

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
                # raise exception if wranglers declared the job a failure
                if job.declare_status is False:
                    raise StimelaRecipeExecutionError("job declared as failed")

                self.log2recipe(job, recipe, step, 'completed')
                self.completed.append(job)

                finished_time = datetime.now()
                job.log.info('job complete at {} after {}'.format(finished_time, finished_time-start_time),
                              # the extra attributes are filtered by e.g. the CARACal logger
                              extra=dict(stimela_job_state=(job.name, "complete")))

            except (utils.StimelaCabRuntimeError,
                    StimelaRecipeExecutionError,
                    StimelaCabParameterError) as exc:
                # ignore exceptions if wranglers declared the job a success
                if job.declare_status is True:
                    finished_time = datetime.now()
                    job.log.info('job complete (declared successful) at {} after {}'.format(finished_time, finished_time - start_time),
                                 # the extra attributes are filtered by e.g. the CARACal logger
                                 extra=dict(stimela_job_state=(job.name, "complete")))
                    continue

                self.remaining = [jb[1] for jb in jobs[i+1:]]
                self.failed = job

                finished_time = datetime.now()
                job.log.error(str(exc), extra=dict(stimela_job_state=(job.name, "failed"), boldface=True))
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
                raise PipelineException(exc, self.completed, job, self.remaining) from None

        self.log.info(
            'Saving pipeline information in {}'.format(self.resume_file))
        utils.writeJson(self.resume_file, recipe)
        self.log.info('Recipe executed successfully')

        return 0

    def close(self):
        """Call this to explicitly close the recipe and clean up. Don't call run() after close()!"""
        for job in self.jobs:
            job.close()
        if os.path.exists(self.workdir):
            shutil.rmtree(self.workdir)
        if self._log_fh is not None:
            self._log_fh.close()

    def __del__(self):
        """Failsafe"""
        self.close()
