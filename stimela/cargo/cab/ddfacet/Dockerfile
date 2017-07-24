FROM stimela/ddfacet:0.2.9
MAINTAINER <sphemakh@gmail.com>
ENV TERM xterm
ADD src /code
ENV LOGFILE ${OUTPUT}/logfile.txt
ENTRYPOINT ["/bin/sh"]
CMD ["-c", "/code/run.sh"]
