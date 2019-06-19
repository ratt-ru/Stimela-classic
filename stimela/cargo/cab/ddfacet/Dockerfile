FROM stimela/ddfacet:ddf0.4.1
MAINTAINER <sphemakh@gmail.com>
ENV TERM xterm
ADD src /scratch/code
ENV LOGFILE ${OUTPUT}/logfile.txt
ENTRYPOINT ["/bin/sh"]
CMD ["-c", "/scratch/code/run.sh"]
