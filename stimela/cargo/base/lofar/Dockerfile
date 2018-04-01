FROM stimela/base:0.3.2
RUN docker-apt-install lofar python-tigger
RUN pip install --upgrade git+https://github.com/ska-sa/tigger
RUN pip install astropy
RUN docker-apt-install gfortran build-essential libboost-python-dev
RUN pip install git+https://github.com/lofar-astron/PyBDSF.git@v1.8.13
