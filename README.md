# Penthesilea

Tools for flexible and system independent (as much docker allows) radio interferometric simulations and reductions.
The main goal of this project is to test the feasibilty of using the AWS system to do SKA1-MID scale simulations and reductions. The simulations and reduction framework is largely based on [Pyxis](https://github.com/ska-sa/pyxis) and [Docker](https://www.docker.com/).

The docker images for this project can be found at: https://hub.docker.com/u/penthesilea

This project is funded by the [SKA/AWS Astrocompute in the cloud ](https://www.skatelescope.org/ska-aws-astrocompute-call-for-proposals) initiative. 


## Requires 
* [Docker](http://docs.docker.com/)
* Python

## Install
Download the repo.
```
git clone https://github.com/SpheMakh/Penthesilea
```
Then install
```
cd Penthesilea
python setup.py install --record files.txt
penthesilea -pull # This will take some time
penthesilea -build
```

## Uninstall
```
cd Penthesilea
cat files.txt | xargs rm 
```

See the [wiki](../../wiki/) for tutorials. 
