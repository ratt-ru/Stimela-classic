FROM stimela/base:1.2.5
MAINTAINER <sphemakh@gmail.com>
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.6 10
RUN pip install msutils
RUN python -c "import MSUtils.msutils"
