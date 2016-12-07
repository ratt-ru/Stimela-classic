FROM stimela/base
RUN docker-apt-install meqtrees time
RUN git clone https://github.com/SpheMakh/owlcat
RUN cd owlcat && pip install . --upgrade
ENV MEQTREES_CATTERY_PATH /usr/lib/python2.7/dist-packages/Cattery
