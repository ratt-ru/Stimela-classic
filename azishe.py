import json
import os
import 


def readJson(conf):

    with open(conf) as _std:
        jdict = json.load(_std)

    for key,val in jdict.iteritems():
        if isinstance(val, unicode):
            jdict[key] = val

    return jdict



if __name__=="__main__":

    conf = readJson(CONF):
    
    simms = conf["observation"]
    simulator = conf["simulate"]
    imager = conf["imager"]
