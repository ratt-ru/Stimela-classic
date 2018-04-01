FROM stimela/casa:0.3.2
MAINTAINER <sphemakh@gmail.com>
ADD src /code
ENV LOGFILE ${OUTPUT}/logfile.txt
CMD python /code/run.py 2>&1 | tee -a $LOGFILE ; (exit ${PIPESTATUS[@]})
