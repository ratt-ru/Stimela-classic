FROM stimela/ddfacet:1.0.1
MAINTAINER <sphemakh@gmail.com>
RUN pip install pyyaml
ENV TERM xterm
ADD src /code
ENV LOGFILE ${OUTPUT}/logfile.txt
ENTRYPOINT ["/bin/sh"]
CMD ["-c", "/code/run.sh"]
