FROM stimela/base:1.4.6
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash -
RUN pip install -U pip setuptools
RUN pip install ragavi>=0.3.5
RUN pip install --force-reinstall -U git+https://github.com/o-smirnov/datashader
RUN pip install -I numpy
RUN ragavi-gains -h
RUN ragavi-vis -h
