FROM sphemakh/crasa:5.6.1
RUN docker-apt-install python3-casacore python3 python3-pip git wget
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.5 10
RUN pip3 install --upgrade --force pip
RUN pip install -U pip 
RUN pip install -U crasa pyyaml astropy
RUN pip install git+https://github.com/ratt-ru/scabha@437c4220968079419976a713c2d5d7e67732742b
RUN docker-apt-install xvfb
