FROM stimela/meqtrees:1.2.0
RUN docker-apt-install xvfb
RUN pip install astro-tigger-lsm
COPY xvfb.init.d /etc/init.d/xvfb
RUN chmod 755 /etc/init.d/xvfb
RUN chmod 777 /var/run
ENV DISPLAY :99
