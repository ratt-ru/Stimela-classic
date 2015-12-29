#!/usr/bin/env python

import os
from distutils.core import setup
import cargo

setup(name = "stimela",
    version = cargo.__version__,
    description = "Dockerized radio interferometry scripting framework",
    author = "Sphesihle Makhathini",
    author_email = "Sphesihle Makhathini <sphemakh@gmail.com>",
    url = "https://github.com/sphemakh/Stimela",
    packages = ["stimela", "cargo","stimela/utils"],
    package_data = dict(penthesilea=["data/skymodels/*.lsm.html", 
                                   "configs/*.json",
                                   "data/observatories/*.txt", 
                                   "cab/*/Dockerfile",
                                   "base/*/Dockerfile",
                                   "cab/*/src/*.py", 
                                   "cab/*/src/*.sh",
                                   "cab/*/src/*.json",
                                   "cab/*/src/tdlconf.profiles"]),
    requires = ["docker", "python"],
    scripts = ["bin/" + i for i in os.listdir("bin")], 
    licence = "This program should come with the GNU General Public Licence. "\
            "If not, find it at http://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html",
    classifiers = [],
     )
