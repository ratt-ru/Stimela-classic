#!/bin/bash -ve


if [ -z "$USER" ]; then
    export USER=root
fi

if [ -z "$CONFIG" ]; then 
    export CONFIG="imaging_params.json"
fi

pyxis azishe
