FROM stimela/meqtrees:1.0.1
RUN pip install --no-deps "owlcat>=1.5.4"
RUN docker-apt-install xvfb
COPY xvfb.init.d /etc/init.d/xvfb
RUN chmod 755 /etc/init.d/xvfb
RUN chmod 777 /var/run
ENV DISPLAY :99
ENV MEQTREES_CATTERY_PATH /usr/lib/python2.7/dist-packages/Cattery
