#!/usr/bin/env bash
python /code/run.py 2>&1 | tee -a $LOGFILE 
exit ${PIPESTATUS[0]}
