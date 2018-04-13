FROM stimela/ddfacet:1.0.0
MAINTAINER <sphemakh@gmail.com>
ENV TERM xterm
ADD src /code
ENV LOGFILE ${OUTPUT}/logfile.txt
ENTRYPOINT ["/bin/sh"]
CMD ["-c", "/code/run.sh"]
