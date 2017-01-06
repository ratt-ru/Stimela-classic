#!/usr/bin/python
from pyrap.tables import table as tbl
from pyrap import tables as tbls
import re
import numpy as np

with open("/southern_calibrators.txt") as f, \
     tbl("/casa-release-4.7.0-el6/data/nrao/VLA/standards/fluxcalibrator.data", readonly=False) as fc, \
     tbl("/casa-release-4.7.0-el6/data/nrao/VLA/standards/PerleyButler2013Coeffs", readonly=False) as pb:
    line=f.readline()
    ln_no = 1
    while line:
        #discard comments
        command = line.split("//")[0]

        #empty line ?
        if command.strip() == "":
            print "Skipping line: '%s'" % line
            line = f.readline()
            ln_no += 1
            continue

        #source ?
        valset = re.match(r"^name=(?P<name>[0-9A-Za-z\-+_]+)[ ]+"
                          r"epoch=(?P<epoch>[0-9]+)[ ]+"
                          r"ra=(?P<ra>[+\-]?[0-9]+h[0-9]+m[0-9]+(?:.[0-9]+)?s)[ ]+"
                          r"dec=(?P<decl>[+\-]?[0-9]+d[0-9]+m[0-9]+(?:.[0-9]+)?s)[ ]+"
                          r"a=(?P<a>[+\-]?[0-9]+(?:.[0-9]+)?)[ ]+"
                          r"b=(?P<b>[+\-]?[0-9]+(?:.[0-9]+)?)[ ]+"
                          r"c=(?P<c>[+\-]?[0-9]+(?:.[0-9]+)?)[ ]+"
                          r"d=(?P<d>[+\-]?[0-9]+(?:.[0-9]+)?)$", 
                          command)
        #else illegal
        if not valset:
            raise RuntimeError("Illegal line encountered "
                               "at line %d:'%s'" % (ln_no, line))

        # parse sources (spectra in MHz) 
        name = valset.group("name")
        epoch = int(valset.group("epoch"))
        ra = valset.group("ra")
        valset_ra = re.match(r"^(?P<h>[+\-]?[0-9]+)h"
                             r"(?P<m>[0-9]+)m"
                             r"(?P<s>[0-9]+(?:.[0-9]+)?)s$",
                             ra)
        ra = np.deg2rad((float(valset_ra.group("h")) +
                         float(valset_ra.group("m")) / 60.0 +
                         float(valset_ra.group("s")) / 3600) / 24.0 * 360)
        decl = valset.group("decl")
        valset_decl = re.match(r"^(?P<d>[+\-]?[0-9]+)d"
                               r"(?P<m>[0-9]+)m"
                               r"(?P<s>[0-9]+(?:.[0-9]+)?)s$",
                               decl)
        decl = np.deg2rad(float(valset_decl.group("d")) + \
                          float(valset_decl.group("m")) + \
                          float(valset_decl.group("s")))

        a = float(valset.group("a"))
        b = float(valset.group("b"))
        c = float(valset.group("c"))
        d = float(valset.group("d"))
        
        # convert models to Perley Butler GHz format
        k = np.log10(1000)
        a1 = a + (b * k) + (c * k ** 2) + (d * k ** 3)
        b1 = b + (2 * c * k) + (3 * d * k ** 2)
        c1 = c + (3 * d * k)
        d1 = d

        print "Adding %s\t%d\t%3.2f\t%3.2f\t%.4f\t%.4f\t%.4f\t%.4f" % \
            (name, epoch, ra, decl, a1, b1, c1, d1)

        # append to standards table
        fc.addrows()
        fc.putcell("Name", fc.nrows() - 1, name)
        fc.putcell("RA_J2000", fc.nrows() - 1, ra)
        fc.putcell("Dec_J2000", fc.nrows() - 1, decl)
        fc.putcell("AltNames", fc.nrows() - 1, np.array([[name]]))

        coeffs = tbls.makearrcoldesc(name + "_coeffs", 
                                     None,
                                     ndim = 1,
                                     shape = [4],
                                     valuetype="float")
        coefferrs = tbls.makearrcoldesc(name + "_coefferrs", 
                                        None,
                                        ndim = 1,
                                        shape = [4],
                                        valuetype="float")
        pb.addcols(coeffs)
        pb.addcols(coefferrs)
        pb.putcol(name + "_coeffs",
                  np.tile(np.array([a1, b1, c1, d1], 
                                   dtype=np.float32),
                          (pb.nrows(), 1)))
        pb.putcol(name + "_coefferrs",
                  np.tile(np.array([0, 0, 0, 0], 
                                   dtype=np.float32),
                          (pb.nrows(), 1)))

        # finally parse next line
        line = f.readline()
        ln_no += 1



