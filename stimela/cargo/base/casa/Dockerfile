FROM sphemakh/crasa:5.6.1
RUN pip install -U pip 
RUN pip install -U crasa pyyaml astropy
ADD xvfb.init.d /etc/init.d 
RUN docker-apt-install xvfb
