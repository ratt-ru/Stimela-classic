FROM bhugo/ddfacet:0.6.0
MAINTAINER Ben Hugo "bhugo@ska.ac.za"
# stimela dependencies
RUN pip3 install pyyaml
RUN apt install xvfb -y
COPY xvfb.init.d /etc/init.d/xvfb
RUN chmod 755 /etc/init.d/xvfb
RUN chmod 777 /var/run
ENV DISPLAY :99
RUN DDF.py --help 
ENTRYPOINT []
