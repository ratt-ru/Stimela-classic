FROM stimela/base:1.2.0
RUN pip install --upgrade pip
RUN pip install owlcat meqtrees-cattery --upgrade --ignore-installed
RUN pip uninstall -y python-casacore
RUN docker-apt-install python-casacore
ENV MEQTREES_CATTERY_PATH /usr/lib/python2.7/dist-packages/Cattery
