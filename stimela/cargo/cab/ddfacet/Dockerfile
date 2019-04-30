FROM stimela/ddfacet:1.0.1
MAINTAINER <sphemakh@gmail.com>
RUN pip install pyyaml
ENV TERM xterm
ADD src /scratch/code
ENV LOGFILE ${OUTPUT}/logfile.txt
RUN chmod -R a+rwx /root
RUN cp -r /root/.local/lib/python2.7/site-packages/* /usr/local/lib/python2.7/dist-packages
RUN python2.7 -c "import google.protobuf"
ENTRYPOINT ["/bin/sh"]
CMD ["-c", "/scratch/code/run.sh"]
