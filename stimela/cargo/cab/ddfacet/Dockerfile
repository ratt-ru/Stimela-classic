FROM stimela/ddfacet:0.2.9
MAINTAINER <sphemakh@gmail.com>
ENV TERM xterm
ADD src /code
ENV LOGFILE ${OUTPUT}/logfile.txt
ENTRYPOINT ["/bin/bash"]
CMD ["-c", "python /code/run.py 2>&1 | tee -a $LOGFILE ; (exit ${PIPESTATUS})"]
