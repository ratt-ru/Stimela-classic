FROM stimela/base:0.3.1
RUN docker-apt-install meqtrees time
RUN pip install --upgrade git+https://github.com/SpheMakh/owlcat
RUN pip install --upgrade git+https://github.com/ska-sa/tigger
RUN pip install --upgrade git+https://github.com/ska-sa/meqtrees-cattery
ENV MEQTREES_CATTERY_PATH /usr/local/lib/python2.7/dist-packages/Cattery
