FROM stimela/meqtrees:0.3.1
MAINTAINER <sphemakh@gmial.com>
ADD src /code
RUN pip install --upgrade  git+https://github.com/Athanaseus/aimfast
ENV LOGFILE ${OUTPUT}/logfile.txt
CMD /code/run.sh

