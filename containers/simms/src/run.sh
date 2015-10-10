#!/bin/bash -ve

if [ -z "$CONFIG" ]; then 
    CONFIG="simms_params.json"
fi

echo $CONFIG
simms -jc $CONFIG
