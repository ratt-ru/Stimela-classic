FROM bhugo/tricolour:0.1.4
MAINTAINER <sphemakh@gmail.com>
RUN echo -e '#!/bin/bash\npython3' > /usr/bin/python && \
    chmod +x /usr/bin/python
RUN pip3 install pyyaml
RUN cp -r /code /opt
ENTRYPOINT [] # PLEASE DONT CHANGE THIS TO ANYTHING ELSE!!!!!

