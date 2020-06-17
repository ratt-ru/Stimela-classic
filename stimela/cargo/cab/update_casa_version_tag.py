import json
import glob
from collections import OrderedDict

for cabfile in glob.glob("casa_*/*.json"):
    with open(cabfile, 'rb') as stdr:
        cabdict = json.load(stdr, object_pairs_hook=OrderedDict)
    cabdict["version"] = ["4.7.2", "5.6.1-8"]
    cabdict["tag"] = ["0.3.0-2", "1.6.3"]
    cabdict["junk"] = ["%s.last" % (cabdict["binary"])]
    with open(cabfile, 'wb') as stdw:
        json.dump(cabdict, stdw, indent=2)

