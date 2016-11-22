import os
import sys

sys.path.append("/utils")
import utils


CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]
OUTDIR = os.environ["OUTPUT"]
MAC_OS = os.environ["MAC_OS"]

if MAC_OS.lower() in ["yes", "true", "yebo", "1"]:
    MAC_OS = True
else:
    MAC_OS = False

jdict = utils.readJson(CONFIG)

# Create options for boolean flags
flags = ["full_pol", "flag_av"]

flags = ['--%s' % (f,) for f, v in (
    (f, jdict.pop(f, False)) for f in flags)
    if v is True]

h5s = ["%s/%s" % (INPUT, n) for n in jdict.pop('hdf5files')]

cmd = [ "--%s %s"%(key, "" if isinstance(val, bool) else val) for (key,val) in jdict.iteritems()]

utils.xrun("h5toms.py", cmd+flags+h5s )
