FROM stimela/rfinder:1.0.1
MAINTAINER <sphemakh@gmial.com>
RUN pip install pillow --upgrade
COPY xvfb.init.d /etc/init.d/xvfb
RUN chmod 755 /etc/init.d/xvfb
RUN chmod 777 /var/run
ENV DISPLAY :99
ADD src /scratch/code
ENV LOGFILE ${OUTPUT}/logfile.txt
CMD /scratch/code/run.sh
