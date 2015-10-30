#!make

PROJECT=penthesilea

.PHONY: all build force-build pull

all: pull

build:  
		docker build -t $(PROJECT)/base containers/base
		docker build -t $(PROJECT)/casapy containers/casapy
		docker build -t $(PROJECT)/simms containers/simms
		docker build -t $(PROJECT)/simulator containers/simulator
		docker build -t $(PROJECT)/predict containers/predict
		docker build -t $(PROJECT)/imager containers/imager
		docker build -t $(PROJECT)/sourcery containers/sourcery
		docker build -t $(PROJECT)/calibrator containers/calibrator

force-build:
		docker build -t $(PROJECT)/base --no-cache=true containers/base
		docker build -t $(PROJECT)/casapy --nocache=true containers/casapy
		docker build -t $(PROJECT)/simms --no-cache=true containers/simms
		docker build -t $(PROJECT)/simulator --no-cache=true containers/simulator
		docker build -t $(PROJECT)/predict --no-cache=true containers/predict
		docker build -t $(PROJECT)/imager --no-cache=true containers/imager
		docker build -t $(PROJECT)/sourcery --no-cache=true containers/sourcery
		docker build -t $(PROJECT)/calibrator --no-cache=true containers/calibrator

pull:
		docker pull $(PROJECT)/base:stable.10.15
		docker pull $(PROJECT)/casapy:stable.10.15
		docker pull $(PROJECT)/simms:stable.10.15
		docker pull $(PROJECT)/simulator
		docker pull $(PROJECT)/predict:stable.10.15
		docker pull $(PROJECT)/imager:stable.10.15
		docker pull $(PROJECT)/sourcery:stable.10.15
