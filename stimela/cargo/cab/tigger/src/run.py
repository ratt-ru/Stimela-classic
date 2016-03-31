import os
import sys
import re

sys.path.append("/utils")
import utils

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]

jdict = utils.readJson(CONFIG)

operation = jdict["operation"]
cmd_ = jdict["command"]

sub = set(re.findall('\{(.*?)\}', cmd_))

cmd = cmd_

for item in map(str, sub):
    cmd = cmd.replace("${%s}"%item, globals()[item])


forced = False
if cmd.find("-f")>0:
   forced = True

utils.xrun(operation, [cmd, "" if forced else "-f"])
