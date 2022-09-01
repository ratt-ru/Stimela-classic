FROM bhugo/ddfacet:0.7.0
MAINTAINER Ben Hugo "bhugo@ska.ac.za"
RUN pip3 install pyyaml
RUN apt update -y
RUN apt install xvfb -y
COPY xvfb.init.d /etc/init.d/xvfb
RUN chmod 755 /etc/init.d/xvfb
RUN chmod 777 /var/run
RUN ln -s /usr/bin/python3 /usr/bin/python
ENV DISPLAY :99
RUN DDF.py --help 
ENTRYPOINT []
