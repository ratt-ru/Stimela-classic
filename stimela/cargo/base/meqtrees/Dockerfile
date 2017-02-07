FROM stimela/base:0.2.5
RUN docker-apt-install meqtrees time
RUN git clone https://github.com/SpheMakh/owlcat
RUN cd owlcat && pip install . --upgrade
ENV MEQTREES_CATTERY_PATH /usr/lib/python2.7/dist-packages/Cattery
RUN pip install --upgrade git+https://github.com/ska-sa/tigger
