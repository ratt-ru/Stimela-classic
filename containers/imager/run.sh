#!/bin/bash -ve

if [ -z "$1" ]; then 
    echo "MS not specified. Aborting"
    exit
else
    MSNAME="$1"
fi


if [ -z "$2" ]; then 
    CONFIG="$2"
else
    CONFIG="imaging_params.json"
fi


if [ -z "$USER" ]; then
    export USER=root
fi

pyxis $MSNAME CFG=$CONFIG OUTDIR=/output azishe
