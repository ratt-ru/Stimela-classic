#!/bin/bash -ve

if [ -z "$CONFIG" ]; then 
    export CONFIG="meqtrees_sim_params.json"
fi

if [ -z "$USER" ]; then
    export USER=root
fi

pyxis $MSNAME OUTDIR=/output azishe
