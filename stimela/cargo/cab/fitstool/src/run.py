import os
import sys

sys.path.append('/utils')
import utils
import json

CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
OUTPUT = os.environ["OUTPUT"]
MSDIR = os.environ["MSDIR"]

jdict = utils.readJson(CONFIG)

imagenames = jdict.pop("image-names")
if isinstance(imagenames, str):
   imagenames = [imagenames]
imagenames = [OUTPUT + "/" + img for img in imagenames]

try:
    output = jdict.pop("output") #output argument of flagms not OUTPUT
    if output is not None:
        assert isinstance(output, (str, unicode)), "msname parameter must be string"
    output = OUTPUT + "/" + output
except:
    output = None

OPT_ARGS = ["--%s %s" % (k, v) for k, v in jdict.iteritems()]
ARGS = [" ".join(imagenames)]
utils.xrun("fitstool.py", OPT_ARGS, ARGS)

