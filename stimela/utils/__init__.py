import os
import json
import tempfile
import inspect
import re
import codecs
import platform

from .xrun_poll import xrun
import stimela.exceptions

# for backwards compatibility
StimelaCabRuntimeError = stimela.exceptions.StimelaCabRuntimeError
CPUS = 1

# Images that are only published for linux/amd64 (CASA and casatools have no
# Linux arm64 releases). Other hosts must ask for the amd64 image explicitly
# and run it under emulation (e.g. Rosetta or QEMU).
AMD64_ONLY_IMAGES = ("stimela/casa", "stimela/wsclean-idg")


def needs_amd64_emulation(image):
    """True if image is amd64-only and this host is not x86_64"""
    if platform.machine().lower() in ("x86_64", "amd64"):
        return False
    name = image.split("://")[-1].rsplit(":", 1)[0]
    return name.endswith(AMD64_ONLY_IMAGES)


def platform_args(image):
    """Extra docker/podman arguments needed to pull or run image on this host"""
    return ["--platform", "linux/amd64"] if needs_amd64_emulation(image) else []

def assign(key, value):
    frame = inspect.currentframe().f_back
    frame.f_globals[key] = value


def readJson(conf):
    with open(conf, "r") as _std:
        jdict = json.load(_std)
        return jdict


def writeJson(config, dictionary):
    with codecs.open(config, "w", "utf8") as std:
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

    temp_dir = tempfile.mkdtemp(prefix="tmp-stimela-{:s}-".format(label), dir=destdir)
    xrun("cp", ["-r", "{:s}/Dockerfile {:s}/src".format(dirname, dirname), temp_dir])

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

    log = string.split(separator)[index - 1]

    images = []

    for line in log.split("\n"):
        if line.find("<=BASE_IMAGE=>") > 0:
            tmp = line.split("<=BASE_IMAGE=>")[-1]
            image, base = tmp.split("=")
            images.append((image.strip(), base))

    return images


def substitute_globals(string, globs=None):
    sub = set(re.findall(r"\{(.*?)\}", string))
    globs = globs or inspect.currentframe().f_back.f_globals
    if sub:
        for item in map(str, sub):
            string = string.replace("${%s}" % item, globs[item])
        return string
    else:
        return False
