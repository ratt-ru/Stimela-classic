import os
import sys
import json
import yaml
import time
import tempfile
import inspect
import warnings
import re
import math
import codecs

class StimelaCabRuntimeError(RuntimeError):
    pass

class StimelaProcessRuntimeError(RuntimeError):
    pass



CPUS = 1

from .xrun_poll import xrun

def assign(key, value):
    frame = inspect.currentframe().f_back
    frame.f_globals[key] = value


def readJson(conf):
    with open(conf, "r") as _std:
        jdict = yaml.safe_load(_std)
        return jdict


def writeJson(config, dictionary):
    with codecs.open(config, 'w', 'utf8') as std:
        std.write(json.dumps(dictionary, ensure_ascii=False))


def get_Dockerfile_base_image(image):

    if os.path.isfile(image):
        dockerfile = image
    else:
        dockerfile = "{:s}/Dockerfile".format(image)

    with open(dockerfile, "r") as std:
        _from = ""
        for line in std.readlines():
            if line.startswith("FROM"):
                _from = line

    return _from


def change_Dockerfile_base_image(path, _from, label, destdir="."):
    if os.path.isfile(path):
        dockerfile = path
        dirname = os.path.dirname(path)
    else:
        dockerfile = "{:s}/Dockerfile".format(path)
        dirname = path

    with open(dockerfile, "r") as std:
        lines = std.readlines()
        for line in lines:
            if line.startswith("FROM"):
                lines.remove(line)

    temp_dir = tempfile.mkdtemp(
        prefix="tmp-stimela-{:s}-".format(label), dir=destdir)
    xrun(
        "cp", ["-r", "{:s}/Dockerfile {:s}/src".format(dirname, dirname), temp_dir])

    dockerfile = "{:s}/Dockerfile".format(temp_dir)

    with open(dockerfile, "w") as std:
        std.write("{:s}\n".format(_from))

        for line in lines:
            std.write(line)

    return temp_dir, dockerfile


def get_base_images(logfile, index=1):

    with open(logfile, "r") as std:
        string = std.read()

    separator = "[================================DONE==========================]"

    log = string.split(separator)[index-1]

    images = []

    for line in log.split("\n"):
        if line.find("<=BASE_IMAGE=>") > 0:
            tmp = line.split("<=BASE_IMAGE=>")[-1]
            image, base = tmp.split("=")
            images.append((image.strip(), base))

    return images


def substitute_globals(string, globs=None):
    sub = set(re.findall('\{(.*?)\}', string))
    globs = globs or inspect.currentframe().f_back.f_globals
    if sub:
        for item in map(str, sub):
            string = string.replace("${%s}" % item, globs[item])
        return string
    else:
        return False
