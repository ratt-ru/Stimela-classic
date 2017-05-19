FROM stimela/sofia:dev
MAINTAINER <sphemakh@gmial.com>
ADD src /code
ENV LOGFILE ${OUTPUT}/logfile.txt
CMD python /code/run.py 2>&1 | tee -a $LOGFILE ; (exit ${PIPESTATUS})
