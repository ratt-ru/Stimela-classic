# Penthesilea

Tools for flexible and system independent (as much docker allows) radio interferometric simulations and reductions.
The main goal of this project is to test the feasibilty of using the AWS system to do SKA1-MID scale simulations and reductions. The simulations and reduction framework is largely based on [Pyxis](https://github.com/ska-sa/pyxis) and [Docker](https://www.docker.com/).

The docker images for this project can be found at: https://hub.docker.com/u/penthesilea

This project is funded by the [SKA/AWS Astrocompute in the cloud ](https://www.skatelescope.org/ska-aws-astrocompute-call-for-proposals) initiative. 


## Requires 
* [Docker](http://docs.docker.com/)
* Python

## Build
Once you've installed Docker the build Penthesilea
```
cd Penthesilea
make pull # pull base containers
make build # build executor containers
```

See the [wiki](../../wiki/) for tutorials. 
