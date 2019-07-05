FROM bhugo/ddfacet:0.4.1
MAINTAINER Ben Hugo "bhugo@ska.ac.za"
RUN pip install pyyaml
ENTRYPOINT ["/bin/sh","-c"]
RUN ["/usr/local/bin/DDF.py","--help"]
