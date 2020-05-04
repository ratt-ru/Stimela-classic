#!/usr/bin/env python

import os
import sys
from setuptools import setup
import glob


requirements = ["pyyaml",
                "nose>=1.3.7",
                "future-fstrings",
                "udocker",
                ],

PACKAGE_NAME = "stimela"
__version__ = "1.4.3"

setup(name=PACKAGE_NAME,
      version=__version__,
      description="Dockerized radio interferometry scripting framework",
      author="Sphesihle Makhathini",
      author_email="sphemakh@gmail.com",
      url="https://github.com/sphemakh/Stimela",
      packages=["stimela", "stimela/cargo",
                "stimela/utils", "stimela/cargo/cab",
                "stimela/cargo/base"],
      package_data={"stimela/cargo": [
          "cab/*/Dockerfile",
          "base/*/Dockerfile",
          "cab/*/src/*.py",
          "cab/*/src/*.sh",
          "cab/*/src/*.json",
          "base/*/xvfb.init.d",
          "cab/*/xvfb.init.d",
          "cab/*/parameters.json",
          "cab/*/src/tdlconf.profiles",
      ]},
      install_requires=requirements,
      scripts=["bin/" + i for i in os.listdir("bin")] + 
                glob.glob("stimela/cargo/cab/stimela_runscript"),
      classifiers=[],
      )
