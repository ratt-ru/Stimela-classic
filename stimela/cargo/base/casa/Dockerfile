FROM sphemakh/crasa:5.6.1
RUN docker-apt-install python3-casacore python3 python3-pip git wget xvfb
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.5 10
RUN pip3 install --upgrade --force pip
RUN pip install -U pip 
RUN pip install -U crasa pyyaml astropy scabha
