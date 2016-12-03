import os
import sys

sys.path.append("/utils")
import utils


CONFIG = os.environ["CONFIG"]
INPUT = os.environ["INPUT"]
MSDIR = os.environ["MSDIR"]
OUTDIR = os.environ["OUTPUT"]

jdict = utils.readJson(CONFIG)

# Create options for boolean flags
flags = ["full_pol", "flag_av"]

flags = ['--%s' % (f,) for f, v in (
    (f, jdict.pop(f, False)) for f in flags)
    if v is True]

h5s = [os.path.join(INPUT, n) for n in jdict.pop('hdf5files')]

try:
    ms = ["--output-ms %s" % os.path.join(MSDIR, jdict.pop('output-ms'))]
except KeyError:
    files = [os.splitext(os.path.split(f)[1])[0] for f in h5s]
    ms = ["--output-ms %s.ms" % os.path.join(MSDIR, f) for f in files[0:1]]

cmd = [ "--%s %s"%(key, "" if isinstance(val, bool) else val) for (key,val) in jdict.iteritems()]

utils.xrun("h5toms.py", cmd+flags+ms+h5s )
