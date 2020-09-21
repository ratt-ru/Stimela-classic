FROM stimela/base:1.6.6
RUN docker-apt-upgrade
RUN docker-apt-install python-pip python-astro-tigger-lsm pybdsf
RUN rm -f /usr/bin/python && ln -s /usr/bin/python2 /usr/bin/python
RUN pip2 install astropy pyyaml
