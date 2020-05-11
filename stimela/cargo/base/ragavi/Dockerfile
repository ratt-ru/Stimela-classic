FROM stimela/base:1.2.5
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash -
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.6 10
RUN pip3 install -U pip setuptools pyyaml
RUN pip3 install -U python-casacore git+https://github.com/ska-sa/dask-ms@remove-table-proxy-weakref-finalize
#dask-ms==0.2.3
# RUN pip3 install -U ragavi
RUN pip3 install git+https://github.com/ratt-ru/ragavi@dev
# RUN pip install --force-reinstall -U git+https://github.com/o-smirnov/datashader
RUN pip3 install -I numpy
RUN ragavi-gains -h
RUN ragavi-vis -h
#RUN python3 -c "import yaml"
