FROM stimela/meqtrees:1.2.0
RUN docker-apt-install python3-pip \
                       python3-numpy

RUN pip3 install --upgrade aimfast==1.0rc1
RUN pip3 install --upgrade keyring==12.0.0 --force-reinstall
