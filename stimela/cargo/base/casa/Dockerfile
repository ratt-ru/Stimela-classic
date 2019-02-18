FROM stimela/crasa:5.4.1
RUN apt-get -y install xvfb
COPY xvfb.init.d /etc/init.d/xvfb
RUN chmod 755 /etc/init.d/xvfb
RUN chmod 777 /var/run
ENV DISPLAY :99
RUN pip install -U pip 
RUN pip install -U crasa pyyaml
ENV PATH /${PATH}
