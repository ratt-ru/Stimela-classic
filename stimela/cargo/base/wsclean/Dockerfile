FROM stimela/base
RUN docker-apt-install wsclean
RUN docker-apt-install wget
RUN wget http://tenet.dl.sourceforge.net/project/wsclean/wsclean-2.0/wsclean-2.0.tar.bz2
RUN docker-apt-install cmake libcasacore2-dev libcasacore2
RUN tar xfvj wsclean-2.0.tar.bz2 ; cd wsclean-2.0 && mkdir build ; cd build ; cmake .. ; make install 

