import os
import sys

sys.path.append("/utils")
import utils

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

jdict = utils.readJson(CONFIG)

command = jdict.get("command")
inlsm = jdict.pop("inlsm")
outlsm = jdict.pop("outlsm")
append = jdict.pop("append", None)

for item in "inlsm outlsm append image".split():
    if not isinstance(globals()[item], str):
        continue
    tmp = OUTPUT +"/"+ image if item=="outlsm" else INPUT +"/"+ image
    globals()[item] = utils.substitute_globals(globals()[item]) or tmp
        
if append:
    inlsm  = "--append %s"%append

if image:
    image = utils.substitute_globals(image) or INPUT +"/"+image

utils.xrun(command, [args, image, inlsm, outlsm])
