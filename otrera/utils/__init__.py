import subprocess
import os
import sys
import logging
import json
import codecs
import time

from multiprocessing import Process, Manager, Lock
manager = Manager()


def logger(level=0, logfile=None):

    if logfile:
        logging.basicConfig(filename=logfile)
    else:
        logging.basicConfig()

    LOGL = {"0": "INFO",
            "1": "DEBUG",
            "2": "ERROR",
            "3": "CRITICAL"}

    log = logging.getLogger("OTRERA")
    log.setLevel(eval("logging."+LOGL[str(level)]))

    return log


def xrun(command, options, log=None):
    """
        Run something on command line.

        Example: _run("ls", ["-lrt", "../"])
    """

    cmd = " ".join([command]+options)

    if log:
        log.info("Running: %s"%cmd)
    else:
        print('running: %s'%cmd)

    process = subprocess.Popen(cmd,
                  stderr=subprocess.PIPE if not isinstance(sys.stderr,file) else sys.stderr,
                  stdout=subprocess.PIPE if not isinstance(sys.stdout,file) else sys.stdout,
                  shell=True)
    if process.stdout or process.stderr:
        out,err = process.comunicate()
        sys.stdout.write(out)
        sys.stderr.write(err)
        out = None
    else:
        process.wait()
    if process.returncode:
         raise SystemError('%s: returns errr code %d'%(command, process.returncode))


def pper(iterable, command, cpus, stagger=2, logger=None):
    """
       Run command in parallel.
       
       iterable :  argument(s) to iterate over
       command : callable command to run
       cpus : number of cpus to use
       stagger : stagger jobs (in seconds)
       logger : logging instance
    """

    if not hasattr(iterable, "__iter__"):
        raise TypeError("Can not iterate over [%s]. Make its iterable"%iterable)

    if not callable(command):
        raise TypeError("command [%] is not callable"%(command.func_name))

    message = "Iterating over :: %s"%repr(iterable)

    if logger:
        logger.info(message)
    else:
        print message


    active = manager.Value("d", 0)
    
    def worker(*args):
        command(*args)
        active.value -= 1

    nprocs = len(iterable)
    counter = 0
    procs = []

    while counter <= nprocs-1:
        if active.value >= cpus:
            continue
        
        time.sleep(stagger)
        active.value += 1
        args = iterable[counter]

        if not hasattr(args, "__iter__"):
            args = (args,)

        proc = Process(target=worker, args=args)
        procs.append(proc)
        proc.start()
        counter += 1


    for proc in procs:
        proc.join()



def readJson(conf):

   with open(conf) as _std:
       jdict = json.load(_std)

   for key,val in jdict.iteritems():
       if isinstance(val, unicode):
           jdict[key] = val

   return jdict


def writeJson(config, dictionary):
    with codecs.open(config, 'w', 'utf8') as std:
        std.write(json.dumps(dictionary, ensure_ascii=False))
