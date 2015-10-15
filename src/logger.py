#!/usr/bin/env python
import subprocess
import os
import sys

## %prog <logger file> <container> <job>

def _run(command, options):
    cmd = " ".join([command]+options)
    print('running: %s'%cmd)
    process = subprocess.Popen(cmd,
                  stderr=subprocess.PIPE if not isinstance(sys.stderr,file) else sys.stderr,
                  stdout=subprocess.PIPE if not isinstance(sys.stdout,file) else sys.stdout,
                  shell=True)
    if process.stdout or process.stderr:
        out,err = process.comunicate()
        sys.stdout.write(out)
        sys.stderr.write(err)
        out = None
    else:
        process.wait()
    if process.returncode:
         raise SystemError('%s: returns errr code %d'%(command, process.returncode))

log = sys.argv[1]
container = sys.argv[2]
job = sys.argv[3].lower()

if job == "start":
    with open(log, "a") as std:
        std.write("%s 1 1\n"%container)
    sys.exit(0)

with open(log, "r+") as std:

    lines = std.readlines()
    std.seek(0)

    if job in ["stop", "rm"]:
        # Find container in logger
        for line in lines:
            name, created, running = line.split()

            if name == container or container=="all":
                if job == "stop":
                    _run("test", ["`docker inspect -f {{.State.Running}} %s`"%name,
                         "&&", "docker stop", name])
                    std.write("%s 1 0\n"%name)
                else:
                    _run("docker", ["rm", name])
            else:
                std.write(line)
    std.truncate()
