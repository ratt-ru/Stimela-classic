FROM stimela/casa:0.2.5
MAINTAINER <sphemakh@gmail.com>
#This task needs xvfb to be installed
# @sphemakh I'm placing the fix in this 
# cab and not the others, I know it is not nice and
# minimal but it will have to do.
RUN apt-get -y install xvfb
COPY xvfb.init.d /etc/init.d/xvfb
RUN chmod 755 /etc/init.d/xvfb
RUN chmod 777 /var/run
ENV DISPLAY :99
ADD src /code
CMD /bin/bash -c "/etc/init.d/xvfb start && python /code/run.py && /etc/init.d/xvfb stop"
