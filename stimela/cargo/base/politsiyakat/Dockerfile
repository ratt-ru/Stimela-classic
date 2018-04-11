FROM stimela/base:0.3.1
RUN docker-apt-install libfreetype6-dev
RUN docker-apt-install wcslib-dev libcfitsio-dev
RUN docker-apt-install python-casacore
RUN docker-apt-install wget
# compile compatible version of CASACORE from source
RUN wget https://github.com/casacore/casacore/archive/v2.3.0.zip
RUN docker-apt-install unzip cmake
RUN unzip v2.3.0.zip
RUN docker-apt-install build-essential gfortran libboost-python-dev
RUN docker-apt-install flex
RUN docker-apt-install libbison-dev
RUN docker-apt-install libblas-dev
RUN docker-apt-install liblapack-dev
RUN mkdir casacore-2.3.0/build; cd casacore-2.3.0/build; cmake ../; make -j16; make install
RUN pip install pip setuptools wheel virtualenv -U
RUN ln -s /usr/include/freetype2/ft2build.h /usr/include/
#RUN pip install git+http://github.com/bennahugo/politsiyakat.git
RUN pip install politsiyakat==0.3.7
