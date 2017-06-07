#!/usr/bin/env bash
/etc/init.d/xvfb start && python /code/run.py 2>&1 | tee -a $LOGFILE \
&& /etc/init.d/xvfb stop
exit ${PIPESTATUS[@]}
