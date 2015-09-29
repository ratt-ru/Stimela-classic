#!/bin/bash -ve

if [ -z "$1" ]; then 
    echo "MS not specified. Aborting"
    exit
else
    MSNAME="$1"
fi

if [ -z "$USER" ]; then
    export USER=root
fi

pyxis $MSNAME OUTDIR=/output azishe
