FROM stimela/ddfacet:ddf0.4.1
MAINTAINER <sphemakh@gmail.com>
ENV TERM xterm
ADD src /scratch/code
ENV LOGFILE ${OUTPUT}/logfile.txt
RUN chmod -R a+rwx /root
#RUN cp -r /root/.local/lib/python2.7/site-packages/* /usr/local/lib/python2.7/dist-packages
RUN python2.7 -c "import google.protobuf"
ENTRYPOINT ["/bin/sh"]
CMD ["-c", "/scratch/code/run.sh"]
