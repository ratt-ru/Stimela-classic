#!/usr/bin/env python

import os
import sys
from setuptools import setup
import glob


requirements = ["pyyaml",
                "nose>=1.3.7",
                "future-fstrings",
                "scabha"
                ],

PACKAGE_NAME = "stimela"
__version__ = "1.6.5"

setup(name=PACKAGE_NAME,
      version=__version__,
      description="Dockerized radio interferometry scripting framework",
      author="Sphesihle Makhathini & RATT",
      author_email="sphemakh@gmail.com",
      url="https://github.com/ratt-ru/Stimela",
      packages=["stimela", "stimela/cargo",
                "stimela/utils", "stimela/cargo/cab",
                "stimela/cargo/base"],
      package_data={"stimela/cargo": [
          "base/*/Dockerfile",
          "base/*.template",
          "cab/*/src/*.py",
          "cab/*/src/*.json",
          "base/*/xvfb.init.d",
          "cab/*/parameters.json",
          "cab/*/src/tdlconf.profiles",
      ]},
      python_requires='>=3.5',
      install_requires=requirements,
      scripts=["bin/" + i for i in os.listdir("bin")] + 
                glob.glob("stimela/cargo/cab/stimela_runscript"),
      classifiers=[],
      )
