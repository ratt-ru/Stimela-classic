#!/usr/bin/env python

import os

from setuptools import setup

setup(name = "stimela",
    version = "1.4.0",
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
    install_requires = ["pyyaml", 
    "scriptcwl", 
    "toil",
    "cwltool"],
    scripts = ["bin/" + i for i in os.listdir("bin")],
    classifiers = [],
     )
