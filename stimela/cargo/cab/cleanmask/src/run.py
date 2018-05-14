import os
import sys

sys.path.append("/scratch/stimela")
import utils

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]

cab = utils.readJson(CONFIG)
params = cab["parameters"]

args = []
for param in params:
    if param['value'] in [False, None]:
        continue
    elif param['value'] is True:
        arg = "{0}{1}".format(cab["prefix"], param["name"])
    else:
        arg = "{0}{1} {2}".format(cab["prefix"], param["name"], param["value"])

    args.append(arg)

utils.xrun(cab["binary"], args)
