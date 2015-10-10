#!make

PROJECT=penthesilea
INPUT=`pwd`/input
OUTPUT=`pwd`/output

ifndef config
    config=configs/driver.json
endif


.PHONY: all build run force-build

all: build run

build:
		./azishe.py -c $(config) -in "/data" -out "/output" -p $(PROJECT)
		docker build -t $(PROJECT)/base containers/base
		docker build -t $(PROJECT)/simms containers/simms
		docker build -t $(PROJECT)/simulator containers/simulator
		docker build -t $(PROJECT)/imager containers/imager

force-build:
		docker build -t $(PROJECT)/base --no-cache=true containers/base
		docker build -t $(PROJECT)/simms --no-cache=true containers/simms
		docker build -t $(PROJECT)/simulator --no-cache=true containers/simulator
		docker build -t $(PROJECT)/imager --no-cache=true containers/imager
        
run:
		docker run -v $(INPUT):/input:rw -v $(OUTPUT):/output:rw -e INPUT=/input -e OUTPUT=/output -e CONFIG=$(PROJECT)-simms_params.json  $(PROJECT)/simms && \
		docker run -v $(INPUT):/input:rw -v $(OUTPUT):/output:rw -e INPUT=/input -e OUTPUT=/output -e CONFIG=$(PROJECT)-simulator_params.json  $(PROJECT)/simulator && \
		docker run -v $(INPUT):/input:rw -v $(OUTPUT):/output:rw -e INPUT=/input -e OUTPUT=/output -e CONFIG=$(PROJECT)-imager_params.json  $(PROJECT)/imager

stop:
		docker stop $(PROJECT)/base
		docker stop $(PROJECT)/simms 
		docker stop $(PROJECT)/simulator 
		docker stop $(PROJECT)/imager 

stop:
		docker rm $(PROJECT)/simms 
		docker rm $(PROJECT)/simulator 
		docker rm $(PROJECT)/imager 
