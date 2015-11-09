import subprocess
import os
import sys
import logging
import json
import codecs


def logger(level=0):
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
