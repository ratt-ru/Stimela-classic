#!/usr/bin/env bash
/etc/init.d/xvfb start
python /scratch/code/run.py 2>&1 | tee -a $LOGFILE
EXIT_STAT=${PIPESTATUS[0]}
/etc/init.d/xvfb stop
(exit ${PIPESTATUS[0]})
