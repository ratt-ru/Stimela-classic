#!make

PROJECT=penthesilea
PROJECT_LOCAL=ares


.PHONY: all pull build

all: pull build


pull:
		docker pull $(PROJECT)/base:stable.11.15
		docker pull $(PROJECT)/casapy:stable.11.15
		docker pull $(PROJECT)/simms:stable.11.15
		docker pull $(PROJECT)/meqtrees:stable.11.15
		docker pull $(PROJECT)/imager:stable.11.15
		docker pull $(PROJECT)/sourcery:stable.11.15
		docker pull $(PROJECT)/autoflagger:stable.11.15
		docker pull $(PROJECT)/flagms:stable.11.15

build-base:  
		docker build -t $(PROJECT)/base containers/base
		docker build -t $(PROJECT)/casapy containers/casapy
		docker build -t $(PROJECT)/simms containers/simms
		docker build -t $(PROJECT)/meqtrees containers/meqtrees
		docker build -t $(PROJECT)/imager containers/imager
		docker build -t $(PROJECT)/sourcery containers/sourcery
		docker build -t $(PROJECT)/autoflagger containers/autoflagger
		docker build -t $(PROJECT)/flagms containers/flagms

build:  
		docker build -t $(PROJECT_LOCAL)/simms Ares/simms
		docker build -t $(PROJECT_LOCAL)/simulator Ares/simulator
		docker build -t $(PROJECT_LOCAL)/calibrator Ares/calibrator
		docker build -t $(PROJECT_LOCAL)/imager Ares/imager
		docker build -t $(PROJECT_LOCAL)/predict Ares/predict
		docker build -t $(PROJECT_LOCAL)/sourcery Ares/sourcery
		docker build -t $(PROJECT_LOCAL)/subtract Ares/subtract
		docker build -t $(PROJECT_LOCAL)/autoflagger Ares/autoflagger
		docker build -t $(PROJECT_LOCAL)/flagms Ares/flagms



