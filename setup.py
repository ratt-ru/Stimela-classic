#!/usr/bin/env python

import os

try:
  from setuptools import setup
except ImportError as e:
  from distutils.core import setup

import stimela

setup(name = "stimela",
    version = stimela.__version__,
    description = "Dockerized radio interferometry scripting framework",
    author = "Sphesihle Makhathini",
    author_email = "Sphesihle Makhathini <sphemakh@gmail.com>",
    url = "https://github.com/sphemakh/Stimela",
    packages = ["stimela", "stimela/cargo","stimela/utils"],
    package_data = { "stimela/cargo" : ["data/skymodels/*.lsm.html",
                                   "configs/*.json",
                                   "data/observatories/*.txt",
                                   "cab/*/Dockerfile",
                                   "base/*/Dockerfile",
                                   "cab/*/src/*.py",
                                   "cab/*/src/*.sh",
                                   "cab/*/src/*.json",
                                   "cab/*/src/tdlconf.profiles"]},
    requires = ["docker", "python"],
    scripts = ["bin/" + i for i in os.listdir("bin")],
    classifiers = [],
     )
