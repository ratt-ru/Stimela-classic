FROM stimela/aoflagger:0.2.9
MAINTAINER <sphemakh@gmial.com>
ADD src /code
ENV LOGFILE ${OUTPUT}/logfile.txt
CMD python /code/run.py 2>&1 | tee -a $LOGFILE ; (exit ${PIPESTATUS})

