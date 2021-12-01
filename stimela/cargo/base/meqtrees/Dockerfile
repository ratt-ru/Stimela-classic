FROM stimela/base:1.6.0

RUN docker-apt-install libblitz0-dev python3-dev libblas-dev liblapack-dev libqdbm-dev wcslib-dev \
 libfftw3-dev python3-numpy libcfitsio-dev libboost-all-dev libboost-system-dev cmake g++ wget gfortran \
 libncurses5-dev libsofa1-dev bison libbison-dev flex libreadline6-dev python3-pip

RUN pip3 install -U pip setuptools wheel

# casacore wheels no longer work and we need python 3 support, so build from source

#####################################################################
## BUILD CASACORE FROM SOURCE
#####################################################################
RUN mkdir /src
WORKDIR /src
RUN wget https://github.com/casacore/casacore/archive/v3.3.0.tar.gz
RUN tar xvf v3.3.0.tar.gz
RUN mkdir casacore-3.3.0/build
WORKDIR /src/casacore-3.3.0/build
RUN echo hello
RUN cmake -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_BUILD_TYPE=Release -DBUILD_DEPRECATED=ON -DBUILD_PYTHON3=ON -DBUILD_PYTHON=OFF ../
RUN make -j 4
RUN make install
RUN ldconfig
#RUN pip install -U --user --force-reinstall --install-option="--prefix=/usr"  pip setuptools wheel
WORKDIR /src
RUN wget https://github.com/casacore/python-casacore/archive/v3.3.0.tar.gz
RUN tar xvf v3.3.0.tar.gz.1
WORKDIR /src/python-casacore-3.3.0
RUN pip3 install .
WORKDIR /
RUN python3 -c "from pyrap.tables import table as tbl"

#####################################################################
## Get CASACORE ephem data
#####################################################################
RUN mkdir -p /usr/share/casacore/data/
WORKDIR /usr/share/casacore/data/
RUN docker-apt-install rsync
RUN rsync -avz rsync://casa-rsync.nrao.edu/casa-data .

#####################################################################
## BUILD MAKEMS FROM SOURCE AND TEST
#####################################################################
RUN mkdir -p /src/
WORKDIR /src
ENV BUILD /src
RUN wget https://github.com/ska-sa/makems/archive/1.5.3.tar.gz
RUN tar xvf 1.5.3.tar.gz
RUN mkdir -p $BUILD/makems-1.5.3/LOFAR/build/gnu_opt
WORKDIR $BUILD/makems-1.5.3/LOFAR/build/gnu_opt
RUN cmake -DCMAKE_MODULE_PATH:PATH=$BUILD/makems-1.5.3/LOFAR/CMake \
-DUSE_LOG4CPLUS=OFF -DBUILD_TESTING=OFF -DCMAKE_BUILD_TYPE=Release ../..
RUN make -j 4
RUN make install

ENV PATH=/src/makems-1.5.3/LOFAR/build/gnu_opt/CEP/MS/src:${PATH}
WORKDIR $BUILD/makems-1.5.3/test
RUN makems WSRT_makems.cfg

#####################################################################
## BUILD CASArest from source
#####################################################################
WORKDIR /src
RUN docker-apt-install git
RUN wget https://github.com/casacore/casarest/archive/v1.7.0.tar.gz
RUN tar xvf v1.7.0.tar.gz
WORKDIR /src/casarest-1.7.0
RUN mkdir -p build
WORKDIR /src/casarest-1.7.0/build
RUN cmake -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_BUILD_TYPE=Release ../
RUN make -j 4
RUN make install
RUN ldconfig


# add additional Timba dependencies
RUN docker-apt-install python3-pyqt4 python3-pyqt5
WORKDIR /code
RUN git clone https://github.com/ska-sa/meqtrees-cattery.git
RUN pip3 install ./meqtrees-cattery
WORKDIR /src
RUN git clone -b v1.5.0 https://github.com/ska-sa/purr.git
RUN git clone -b v1.6.0 https://github.com/ska-sa/owlcat.git
RUN git clone -b v1.4.3 https://github.com/ska-sa/kittens.git
RUN git clone -b v1.6.0 https://github.com/ska-sa/tigger-lsm.git
RUN git clone -b v1.7.1 https://github.com/ska-sa/pyxis.git

RUN pip3 install ./purr ./owlcat ./kittens ./tigger-lsm
RUN pip3 install -e ./pyxis

WORKDIR /src
RUN git clone -b v1.8.0 https://github.com/ska-sa/meqtrees-timba.git
RUN mkdir /src/meqtrees-timba/build
WORKDIR /src/meqtrees-timba/build
RUN cmake -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_BUILD_TYPE=Release -DENABLE_PYTHON_3=ON ..
RUN make -j4
RUN make install
RUN ldconfig

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.6 2
# basic install tests
RUN flag-ms.py --help
RUN meqtree-pipeliner.py --help
RUN pyxis --help

# run test when built
RUN pip3 install nose
WORKDIR /src/pyxis/Pyxis/recipes/meqtrees-batch-test
RUN python3 -m "nose"
