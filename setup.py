#!/usr/bin/env python

import os

try:
  from setuptools import setup
except ImportError as e:
  from distutils.core import setup

from stimela_misc import version

setup(name = "stimela",
    version = version.version,
    description = "Dockerized radio interferometry scripting framework",
    author = "Sphesihle Makhathini",
    author_email = "Sphesihle Makhathini <sphemakh@gmail.com>",
    url = "https://github.com/sphemakh/Stimela",
    packages = ["stimela","stimela_misc", "stimela/cargo","stimela/utils", "stimela/cargo/cab"],
    package_data = { "stimela/cargo" : ["cab/*/Dockerfile",
                                   "base/*/Dockerfile",
                                   "cab/*/src/*.py",
                                   "cab/*/src/*.sh",
                                   "cab/*/src/*.json",
                                   "cab/*/xvfb.init.d",
                                   "cab/*/parameters.json",
                                   "cab/*/src/tdlconf.profiles"]},
    install_requires = ["pyyaml"],
    scripts = ["bin/" + i for i in os.listdir("bin")],
    classifiers = [],
     )
