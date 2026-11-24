FROM quay.io/stimela/base:1.9.0
MAINTAINER <sphemakh@gmail.com>
# chgcentre ships with WSClean, which KERN 10 packages for amd64 and arm64
RUN docker-apt-install wsclean
RUN command -v chgcentre
