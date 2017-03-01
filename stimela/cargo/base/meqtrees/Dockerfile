FROM stimela/base:0.2.8
RUN docker-apt-install meqtrees time
RUN pip install --upgrade git+https://github.com/SpheMakh/owlcat
ENV MEQTREES_CATTERY_PATH /usr/lib/python2.7/dist-packages/Cattery
RUN pip install --upgrade git+https://github.com/ska-sa/tigger
