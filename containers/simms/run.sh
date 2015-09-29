#!/bin/bash -ve

if [ -z "$CONFIG" ]; then 
    CONFIG="simms_params.json"
fi


if [ -z "$USER" ]; then
    export USER=root
fi

simms -jc $CONFIG
