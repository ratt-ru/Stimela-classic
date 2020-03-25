FROM kernsuite/base:5
RUN docker-apt-install git python-pip git wget xvfb python3-pip
RUN pip install -U pip
RUN pip3 install -U pip
RUN pip install pyyaml
RUN pip3 install pyyaml
COPY xvfb.init.d /etc/init.d/xvfb
RUN chmod 755 /etc/init.d/xvfb
RUN chmod 777 /var/run
ENV DISPLAY :99
