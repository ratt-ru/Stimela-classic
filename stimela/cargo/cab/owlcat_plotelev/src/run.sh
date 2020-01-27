#!/usr/bin/env bash
python /scratch/code/run.py 2>&1 | tee -a $LOGFILE 
EXIT_STAT=${PIPESTATUS[0]}
exit $EXIT_STAT
