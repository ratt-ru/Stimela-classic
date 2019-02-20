#!/usr/bin/env python

import os
from setuptools import setup


PACKAGE_NAME = "stimela"
__version__ = "1.0.1"

setup(name = PACKAGE_NAME,
    version = __version__,
    description = "Dockerized radio interferometry scripting framework",
    author = "Sphesihle Makhathini",
    author_email = "sphemakh@gmail.com",
    url = "https://github.com/sphemakh/Stimela",
    packages = ["stimela","stimela_misc", "stimela/cargo","stimela/utils", "stimela/cargo/cab"],
    package_data = { "stimela/cargo" : [
                                   "cab/*/Dockerfile",
                                   "base/*/Dockerfile",
                                   "cab/*/src/*.py",
                                   "cab/*/src/*.sh",
                                   "cab/*/src/*.json",
                                   "cab/*/xvfb.init.d",
                                   "cab/*/parameters.json",
                                   "cab/*/src/tdlconf.profiles",
                                   "cab/singularity_run",
                                   ]},
    install_requires = ["pyyaml", 
                        "nose>=1.3.7"],
    scripts = ["bin/" + i for i in os.listdir("bin")],
    classifiers = [],
     )
