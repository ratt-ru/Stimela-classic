FROM bhugo/ddfacet:0.4.1
MAINTAINER Ben Hugo "bhugo@ska.ac.za"
RUN pip install pyyaml
RUN apt install xvfb -y
COPY xvfb.init.d /etc/init.d/xvfb
RUN chmod 755 /etc/init.d/xvfb
RUN chmod 777 /var/run
ENV DISPLAY :99 
ENTRYPOINT []
