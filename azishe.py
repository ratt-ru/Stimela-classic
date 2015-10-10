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

    add("-c", "--config", default="configs/driver.json",
            help="Pipeline configuration file [json file]. \
Default is './configs/driver.json'")

    add("-in", "--input", default="/input",
            help="Input folder. All indut files should be \
placed here; beam files, antenna tables, etc.")

    add("-out", "--outdir", default="/output",
            help="Output folder. Pipeline \
output will be dumped here")

    add("-p", "--prefix", default="penthesilea",
            help="Output folder. Pipeline \
output will be dumped here")

    args = parser.parse_args()

    conf = readJson(args.config)
    OBSERVATORIES_PATH = "{:s}/observatories".format(args.input)
    
    msname = conf["sim_id"] + ".MS"

    simms = conf["observation"]
    simulator = conf["simulate"]
    imager = conf["image"]

    skymodel = simulator["skymodel"]
    if skymodel in _KATALOG:
        simulator["skymodel"] = _KATALOG[skymodel]

    simulator["direction"] = simms["direction"]

    simulator["msname"] = msname
    simms["msname"] = msname
    imager["msname"] = msname

    def saveconf(conf, name):
        print name
        with codecs.open(name, 'w', 'utf8') as std:
            std.write(json.dumps(conf, ensure_ascii=False))

    tel = simms["tel"]
    simms["tel"] = "{:s}".format(_OBS[tel])
    simms["pos"] = "{:s}/{:s}".format(OBSERVATORIES_PATH, _ANT[tel])

    if os.path.isdir(simms["pos"]):
        simms["pos_type"] = "ascii"

    # Setup data transfer between jobs
    simms["outdir"] = args.outdir
    simulator["indir"] = args.input
    simulator["outdir"] = args.outdir
    imager["indir"] = args.outdir
    imager["outdir"] = args.outdir

    # Save configurations in respective places
    saveconf(simms, 
             "containers/simms/src/{:s}-simms_params.json".format(args.prefix))

    saveconf(simulator, 
             "containers/simulator/src/{:s}-simulator_params.json".format(args.prefix))

    saveconf(imager, 
             "containers/imager/src/{:s}-imager_params.json".format(args.prefix))
