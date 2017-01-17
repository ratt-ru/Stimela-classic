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
inimage = jdict.pop("image", None)
outimage = jdict.pop("output_image", None)

for item in "inlsm outlsm append image".split():
    if not isinstance(globals()[item], str):
        continue
    tmp = OUTPUT +"/"+ image if item=="outlsm" else INPUT +"/"+ image
    globals()[item] = utils.substitute_globals(globals()[item]) or tmp
        
utils.xrun("fitstool.py", [args, image, inlsm, outlsm])
