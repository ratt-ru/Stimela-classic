FROM bhugo/ddfacet:0.5.2
MAINTAINER Ben Hugo "bhugo@ska.ac.za"
RUN rm /usr/local/lib/python3.6/dist-packages/scipy -rf
RUN pip install -U --force-reinstall scipy==1.3.3
RUN pip3 install pyyaml
RUN rm /usr/bin/python
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN apt install xvfb -y
COPY xvfb.init.d /etc/init.d/xvfb
RUN chmod 755 /etc/init.d/xvfb
RUN chmod 777 /var/run
ENV DISPLAY :99
RUN DDF.py --help 
ENTRYPOINT []
