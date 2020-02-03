#!/usr/bin/env bash
python /scratch/code/run.py 2>&1 | tee -a $LOGFILE 
(exit ${PIPESTATUS[0]})
