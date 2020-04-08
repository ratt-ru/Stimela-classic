FROM sphemakh/crasa:5.6.1
RUN docker-apt-install python-casacore
RUN pip install -U pip 
RUN pip install -U crasa pyyaml astropy
ADD xvfb.init.d /etc/init.d 
RUN chmod 755 /etc/init.d/xvfb
RUN chmod 777 /var/run
ENV DISPLAY :99
RUN docker-apt-install xvfb
