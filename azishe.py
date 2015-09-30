import json
import os
import codecs


CONFIG = os.environ["PENTHESILEA_CONF"]
INDIR = os.environ["INDIR"]
OUTDIR = os.environ["OUTDIR"]
STORAGE = os.environ["STORAGE"]

CONFIGS_PATH = "configs"
DATA_PATH = "data"
OBSERVATORIES_PATH = "{:s}/observatories".format(DATA_PATH)


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


def readJson(conf):

    with open(conf) as _std:
        jdict = json.load(_std)

    for key,val in jdict.iteritems():
        if isinstance(val, unicode):
            jdict[key] = val

    return jdict


if __name__=="__main__":

   conf = readJson(CONFIG):
    
    msname = conf["sim_id"] + ".MS"

    simms = conf["observation"]
    simulator = conf["simulate"]
    imager = conf["imager"]

    def saveconf(conf, name):
        with codecs.open(name, 'w', 'utf8') as std:
            std.write(json.dumps(conf, ensure_ascii=False))

    tel = simms["tel"]
    simms["tel"] = "{:s}".format(_OBS[tel])
    simms["pos"] = "{:s}/{:s}".format(OBSERVATORIES_PATH, _ANT[tel])

    if os.path.isdir(simms["pos"]):
        simms["pos_type"] = "ascii"

    # Setup data transfer between jobs
    simms["oudir"] = STORAGE
    simulator["indir"] = STORAGE
    simulator["outdir"] = STORAGE
    imager["indir"] = STORAGE
    imager["outdir"] = STORAGE

    # Save configurations in respective places
    saveconf(simms, 
             "{:s}/simms_params.json".format(CONFIGS_PATH))

    saveconf(simulator, 
             "{:s}/simulator_params.json".format(CONFIGS_PATH))

    saveconf(imager, 
             "{:s}/imaging_params.json".format(CONFIGS_PATH))
