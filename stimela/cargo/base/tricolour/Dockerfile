FROM bhugo/tricolour:0.1.6
MAINTAINER <sphemakh@gmail.com>
RUN pip3 install pyyaml
RUN cp -r /code /opt
RUN docker-apt-install xvfb
COPY xvfb.init.d /etc/init.d/xvfb
RUN rm /usr/bin/python
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN chmod 755 /etc/init.d/xvfb
RUN chmod 777 /var/run
ENV DISPLAY :99
ENTRYPOINT [] # PLEASE DONT CHANGE THIS TO ANYTHING ELSE!!!!!

