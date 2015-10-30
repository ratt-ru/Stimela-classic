import os
import sys
import json
import pyfits
import codecs
import subprocess

CONFIG = os.environ["CONFIG"]
INDIR = os.environ["INPUT"]
OUTDIR = os.environ["OUTPUT"]


def _run(command, options):
    cmd = " ".join([command]+options)
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
            raise SystemError('%s: returns errr code %d'%(command,process.returncode))

def readJson(conf):

    with open(conf) as _std:
        jdict = json.load(_std)

    for key,val in jdict.iteritems():
        if isinstance(val, unicode):
            jdict[key] = str(val)

    return jdict

jdict = readJson(CONFIG)
template = readJson("sourcery_template.json")

name = OUTDIR+"/"+jdict["imagename"]
psf = OUTDIR+"/"+jdict["psf"]

template["imagename"] = name
template["psfname"] = psf
template["reliability"]["thresh_pix"] = jdict["thresh"]
template["outdir"] = OUTDIR

config = "run_me_now.json"
with codecs.open(config, "w", "utf8") as std:
    std.write( json.dumps(template, ensure_ascii=False) )
_run("sourcery", ["-jc", config])

_run("rm", ["-f", config])
