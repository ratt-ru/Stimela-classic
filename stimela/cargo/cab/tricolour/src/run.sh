#!/usr/bin/env bash
/usr/bin/env python3 /scratch/code/run.py 2>&1 | tee -a $LOGFILE 
(exit ${PIPESTATUS[0]})
