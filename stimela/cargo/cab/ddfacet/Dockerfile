FROM stimela/ddfacet:1.1.0
MAINTAINER <sphemakh@gmail.com>
ENV TERM xterm
ADD src /scratch/code
ENV LOGFILE ${OUTPUT}/logfile.txt
ENTRYPOINT ["/bin/sh"]
CMD ["-c", "/scratch/code/run.sh"]
