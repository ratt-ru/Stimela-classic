FROM stimela/base:1.6.0
RUN docker-apt-install gfortran libboost-python-dev libboost-numpy-dev
RUN pip install pip -U
RUN pip install numpy scipy
RUN pip install astropy astro-tigger-lsm git+https://github.com/lofar-astron/PyBDSF
