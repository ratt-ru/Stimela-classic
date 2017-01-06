FROM kernsuite/casa:4.7
COPY standards_amend.py /
COPY southern_calibrators.txt /
RUN apt-get update
RUN apt-get -y install python-casacore
RUN /standards_amend.py
