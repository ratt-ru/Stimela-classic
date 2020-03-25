FROM stimela/base:1.2.5
MAINTAINER <sphemakh@gmail.com>
RUN pip3 install msutils
RUN mv /usr/bin/python /usr/bin/python2
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN python -c "import MSUtils"
