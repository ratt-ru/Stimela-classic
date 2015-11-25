# Penthesilea

Tools for flexible and system independent (as much docker allows) radio interferometric simulations and reductions.
The main goal of this project is to test the feasibilty of using the AWS system to do SKA1-MID scale simulations and reductions. The simulations and reduction framework is largely based on [Pyxis](https://github.com/ska-sa/pyxis) and [Docker](https://www.docker.com/).

This project is funded by the [SKA/AWS Astrocompute in the cloud ](https://www.skatelescope.org/ska-aws-astrocompute-call-for-proposals) initiative. 

## Overview
This project is centred around two sets of docker images, i) *base images* have the required software tools installed in them, then ii) very light weight *executor images* are based on the *base* images and perform radio inteferometry related tasks like imaging, telescope simulations, and calibration. The base images can either be built locally or pulled from [docker hub](https://hub.docker.com/u/penthesilea), and the executor images must be built locally. Note that the (fairly heavy) base images have to be pulled/built very rarely.


**Base Images**
* base - This image has the [radio-satro ppa](https://launchpad.net/~radio-astro/+archive/ubuntu/main) installed, as weel as standard packages such as git, python-pip etc.  
* casapy - This is a CASA image. [its huge](http://thepracticingcatholic.com/wp-content/uploads/2013/08/donald-trump-and-hedge-fund-manager-marc-lasry-will-launch-an-online-gambling-venture-once-its-legalized.jpg)
* imager - This image has imaging packages installed (lwimager, wsclean, CASA)
* simms - Has the the empty visibility creation tool, *simms* installed
* meqtrees - This is a MeqTrees image
* autoflagger - Has automatic flagging tools instaleld (only has aoflagger for now)
* sourcery - This image has source finding related packages



**Executor Images** (a.k.a **ares**)
* simms - Creates visibility datasets
* simulator - Simulates a component sky mode into an MS
* predict - Simulates a FITS image sky model into an MS
* subtract - Subtracts a component sky model from an MS
* calibrator - Self-Calibrates an MS
* sourcery - Runs a source-finder on a FITS image
* autoflagger - Automatically flags an MS
* flagms - Manually flags an MS

Each of these executor images has an execution script (generally a pyxis script) which performs the given task.







## Requires 
* [Docker](http://docs.docker.com/)
* Python

## Install
```
pip install penthesilea
```

Or

Download the repo.
```
git clone https://github.com/SpheMakh/Penthesilea
```
Then install
```
cd Penthesilea
python setup.py install
penthesilea -pull # This will take some time
penthesilea -build
```

## Uninstall
```
pip uninstall penthesilea
```

See the [wiki](../../wiki/) for tutorials. 
