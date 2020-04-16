import os
import sys
import logging
import Crasa.Crasa as crasa

HOME = os.environ["HOME"]
sys.path.append(os.path.join(HOME,"/stimela"))

print(sys.path)

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

cab = utils.readJson(CONFIG)

args = {}
for param in cab['parameters']:
    name = param['name']
    value = param['value']

    if value is None:
        continue

    args[name] = value

task = crasa.CasaTask(cab["binary"], **args)
task.run()
