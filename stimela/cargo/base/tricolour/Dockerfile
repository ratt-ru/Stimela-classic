FROM bhugo/tricolour:0.1.4
MAINTAINER <sphemakh@gmail.com>
RUN echo -e '#!/bin/bash\npython3' > /usr/bin/python && \
    chmod +x /usr/bin/python
RUN alias
ENTRYPOINT ["/bin/bash", "-c"]

RUN pip3 install pyyaml

ENTRYPOINT []
