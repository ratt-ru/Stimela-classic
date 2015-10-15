#!/usr/bin/env python

import json
import os
import codecs
from argparse import ArgumentParser

# Antenna position
# files
_ANT = {
      'meerkat' :  'MeerKAT64_ANTENNAS',
      'kat-7'   :  'KAT7_ANTENNAS',
      'jvla-a'  :  'vlaa.itrf.txt',
      'jvla-b'  :  'vlab.itrf.txt',
      'jvla-c'  :  'vlac.itrf.txt',
      'jvla-d'  :  'vlad.itrf.txt',
      'wsrt'    :  'WSRT_ANTENNAS',
      'ska197'  :  'SKA197_ANTENNAS',
      'ska254'  :  'SKA254_ANTENNAS',
}


# Map to CASA
# names
_OBS = { "meerkat"  :  "meerkat",
         "kat-7"    :  "kat-7",
         "jvla-a"   :  "vla",
         "jvla-b"   :  "vla",
         "jvla-c"   :  "vla",
         "jvla-d"   :  "vla",
         "wsrt"     :  "wsrt",
         "ska197"   :  "meerkat",
         "ska254"   :  "meerkat",
}


_KATALOG = {
        'nvss1deg'  :   'nvss1deg.lsm.html',
        'scubed1deg':   'scubed1deg.lsm.html',
        'cosmos'    :   'COSMOS_NVSS_model.lsm.html',
        'ecdfs'     :   'ECDFS_NVSS_model.lsm.html',
        'xmm-lss'   :   'XMM-LSS_NVSS_model.lsm.html'
}

def readJson(conf):

    with open(conf) as _std:
        jdict = json.load(_std)

    for key,val in jdict.iteritems():
        if isinstance(val, unicode):
            jdict[key] = val

    return jdict


if __name__=="__main__":

    parser = ArgumentParser(description="Parse config file and folders to penthesilea")

    add = parser.add_argument

    add("-c", "--config", default="input/configs/driver.json",
            help="Pipeline configuration file [json file]. \
Default is './configs/driver.json'")

    add("-in", "--input", default="input",
            help="Input folder. All indut files should be \
placed here; beam files, antenna tables, etc.")

    add("-out", "--outdir", default="output",
            help="Output folder. Pipeline \
output will be dumped here")

    add("-p", "--prefix", default="penthesilea",
            help="Output folder. Pipeline \
output will be dumped here")

    add("-dl", "--docker-logger", dest="docker_logger",
            default="src/.penthesilea.log",
            help="Docker logger")

    add("-ts", "--time-stamp", dest="time_stamp",
            help="Time stamp for containers")


    args = parser.parse_args()

    conf = readJson(args.config)
    OBSERVATORIES_PATH = "/input/observatories"
    
    msname = conf["sim_id"] + ".MS"

    simms = conf["observation"]
    simulator = conf["simulate"]
    imager = conf["image"]
    sourcery = conf["sourcery"]


    # setting up sourcery
    imagename = "results-{:s}-{:s}.restored.fits".format(conf["sim_id"],
                imager["imager"])

    imager["imagename"] = imagename

    if sourcery["enable"]:
        sourcery["imagename"] = imagename

    skymodel = simulator["skymodel"]

    ext = skymodel.split(".")[-1]
    predict = False
    comp = None
    if ext in ["fits", "FITS"]:
        predict = True
        if simulator["add_component_model"]:
            comp = simulator["add_component_model"]
            if comp in _KATALOG:
                comp = _KATALOG[comp]
                simulator["add_component_model"] = True
            

    if skymodel in _KATALOG and not predict:
        simulator["skymodel"] = _KATALOG[skymodel]

    simulator["direction"] = simms["direction"]

    simulator["msname"] = msname
    simms["msname"] = "/output/"+msname
    imager["msname"] = msname

    if predict:
        simms["predict"] = True
        simms["skymodel"] = skymodel

    def saveconf(conf, name):
        with codecs.open(name, 'w', 'utf8') as std:
            std.write(json.dumps(conf, ensure_ascii=False))

    tel = simms["tel"]
    simms["tel"] = "{:s}".format(_OBS[tel])
    simms["pos"] = "{:s}/{:s}".format(OBSERVATORIES_PATH, _ANT[tel])

    if os.path.isdir(simms["pos"]):
        simms["pos_type"] = "ascii"

    def docker_run(name, image, config, time_stamp):

        name += "_"+time_stamp

        cmd = "`pwd`/src/logger.py {:s} {:s} start && \\\n".format(args.docker_logger, name)
        cmd += "docker run -v {:s}:/input:rw -v {:s}:/output:rw \
-e INPUT=/input -e OUTPUT=/output -e CONFIG={:s} --name {:s} \
{:s} && \\\n".format(args.input, args.outdir, config, name, image)
        
        _args = [args.docker_logger]*4
        cmd += "`pwd`/src/logger.py {:s} {:s} stop && \\\n".format(args.docker_logger, name)
        return cmd

    run_script = "#!/bin/sh -ve \n##Auto generated\n \n"

    def _run(tag, conf, run_script):

        _conf = "/input/configs/{:s}_params.json".format(tag)
        saveconf(conf, _conf[1:])
        return docker_run(tag, "penthesilea/"+tag, _conf, args.time_stamp)

    # Run simms container
    run_script += _run("simms", simms, run_script)
    # Run simulator/predict
    run_script += _run("predict" if predict else "simulator", simulator, run_script)
    if comp:
        simulator["skymodel"] = comp
        simulator["addnoise"] = False
        run_script += _run("simulator", simulator, run_script)

    # Run imager
    run_script += _run("imager", imager, run_script)
    # Run imager
    if sourcery["enable"]:
        run_script += _run("sourcery", sourcery, run_script)

    with open("src/run.sh", "w") as run_std:
        run_std.write(run_script[:-5])
