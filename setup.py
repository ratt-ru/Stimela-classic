#!/usr/bin/env python

import os
import sys
from setuptools import setup


requirements = ["pyyaml",
                "nose>=1.3.7",
                "future",
                ],

if sys.version_info <= (3, 0):
    requirements += [
        "udocker",
    ],

PACKAGE_NAME = "stimela"
__version__ = "1.2.3"

setup(name=PACKAGE_NAME,
      version=__version__,
      description="Dockerized radio interferometry scripting framework",
      author="Sphesihle Makhathini",
      author_email="sphemakh@gmail.com",
      url="https://github.com/sphemakh/Stimela",
      packages=["stimela", "stimela_misc", "stimela/cargo",
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
          "cab/singularity_run",
          "cab/docker_run",
      ]},
      install_requires=requirements,
      scripts=["bin/" + i for i in os.listdir("bin")],
      classifiers=[],
      )
