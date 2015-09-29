#!/bin/bash -ve

if [ -z "$1" ]; then 
    CONFIG="$1"
else
    CONFIG="simms_params.json"
fi


if [ -z "$USER" ]; then
    export USER=root
fi

simms -jc $CONFIG
