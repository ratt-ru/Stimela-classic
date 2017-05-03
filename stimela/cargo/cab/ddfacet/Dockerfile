FROM stimela/ddfacet
MAINTAINER <sphemakh@gmail.com>
ENV TERM xterm
ADD src /code
ENV LOGFILE ${OUTPUT}/logfile.txt
CMD python /code/run.py 2>&1 | tee -a $LOGFILE ; (exit ${PIPESTATUS})
