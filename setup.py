#!/usr/bin/env python

import os
from distutils.core import setup
import penthesilea

setup(name = "penthesilea",
    version = penthesilea.__version__,
    description = "Dockerized radio interferometry scripting framework",
    author = "Sphesihle Makhathini",
    author_email = "Sphesihle Makhathini <sphemakh@gmail.com>",
    url = "https://github.com/sphemakh/Penthesilea",
    packages = ["otrera", "penthesilea","otrera/utils"],
    package_data = dict(penthesilea=["data/skymodels/*.lsm.html", 
                                   "configs/*.json",
                                   "data/observatories/*.txt", 
                                   "ares/*/Dockerfile",
                                   "base/*/Dockerfile",
                                   "ares/*/src/*.py", 
                                   "ares/*/src/*.sh",
                                   "ares/*/src/*.json",
                                   "ares/*/src/tdlconf.profiles"]),
    requires = ["docker", "python", "make"],
    scripts = ["bin/" + i for i in os.listdir("bin")], 
    licence = "This program should come with the GNU General Public Licence. "\
            "If not, find it at http://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html",
    classifiers = [],
     )
