import os
import sys

sys.path.append("/utils")
import utils


CONFIG = os.environ["CONFIG"]
INDIR = os.environ["INPUT"]
OUTDIR = os.environ["OUTPUT"]
MAC_OS = os.environ["MAC_OS"]

if MAC_OS.lower() in ["yes", "true", "yebo", "1"]:
    MAC_OS = True
else:
    MAC_OS = False

jdict = utils.readJson(CONFIG)


dirty = jdict.pop("dirty_image", None)
psf = jdict.pop("psf_image", None)
if psf==None or dirty==None:
    raise RuntimeError("Need bothe the dirty image and the PSF to procees")

prefix = OUTDIR + "/" + jdict.pop("prefix", dirty[:-5] )

dirty = "%s/%s"%(INDIR, dirty)
psf = "%s/%s"%(INDIR, psf)

cmd = [ "--%s %s"%(key, "" if isinstance(val, bool) else val) for (key,val) in jdict.iteritems()]

utils.xrun("runsane", cmd+[dirty, psf, prefix] )
