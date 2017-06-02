FROM stimela/tigger:0.2.9
MAINTAINER <sphemakh@gmail.com>
ENV MEQTREES_CATTERY_PATH /usr/lib/python2.7/dist-packages/Cattery
ADD src /code
ENV LOGFILE ${OUTPUT}/logfile.txt
CMD python /code/run.py 2>&1 | tee -a $LOGFILE ; (exit ${PIPESTATUS})
