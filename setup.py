#!/usr/bin/env python

import os

try:
  from setuptools import setup
except ImportError as e:
  from distutils.core import setup

setup(name = "stimela",
    version = "1.1.0",
    description = "Dockerized radio interferometry scripting framework",
    author = "Sphesihle Makhathini",
    author_email = "sphemakh@gmail.com",
    url = "https://github.com/sphemakh/Stimela",
    packages = ["stimela","stimela_misc", "stimela/cargo", "stimela/cargo/cab"],
    package_data = { "stimela/cargo" : ["cab/*/Dockerfile",
                                   "base/*/Dockerfile",
                                   "cab/*.cwl",
                                   "cab//types/*.yml",
                                   ]
                   },
    install_requires = ["pyyaml", "scriptcwl", "toil"],
    scripts = ["bin/" + i for i in os.listdir("bin")],
    classifiers = [],
     )
