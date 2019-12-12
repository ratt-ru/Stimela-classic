FROM stimela/meqtrees:1.2.0
RUN pip install -U pip
RUN pip install --no-deps git+https://github.com/ska-sa/owlcat.git@elevation-plots
COPY xvfb.init.d /etc/init.d/xvfb
RUN chmod 755 /etc/init.d/xvfb
RUN chmod 777 /var/run
ENV DISPLAY :99
ENV MEQTREES_CATTERY_PATH /usr/lib/python2.7/dist-packages/Cattery
