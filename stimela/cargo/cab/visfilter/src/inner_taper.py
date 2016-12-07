import matplotlib
matplotlib.use('Agg')

import numpy as np
from pyrap.tables import table
import sys,os
import pylab as plt
from optparse import OptionParser
import time
matplotlib.rcParams.update({'font.size': 22})

def info(string):
  t = "%d/%d/%d %d:%d:%d"%(time.localtime()[:6])
  print "%s ##INFO: %s"%(t,string)
def abort(string):
  t = "%d/%d/%d %d:%d:%d"%(time.localtime()[:6])
  print "%s ##ABORT: %s"%(t,string)
  sys.exit()

def taper(msname, wc=None,res=None,freq=None, savefig=None):
  tab = table(msname, readonly=False)

  bt = lambda w,wc,ws,n: np.sqrt( 1./( 1 + (wc/(w-ws))**(2.0*n) ) ) # using butterworth function to create weights
  sign = -1.0

  if len(res or [0])>1 or len(wc or [0] )>1:
    if wc is None:
      res = np.array(res)
      res = (res/3600.) * np.pi/180. # Convert resolution to radians
      wc = 1.22*((2.998e8/freq)/res)/2. # Zen master of the universe (Oleg) says divide by 2
      wc = wc[np.argsort(wc)]
    ws = (wc[1] - wc[0])/2. + wc[0]
    wc = (wc[1] - wc[0])/2.
  else:

   ws,sign = 0,1.0

   if wc is None:
     try: 
      res = res[0]
      res = (res/3600.) * np.pi/180 # Convert resolution to radians
     except TypeError: abort("Either of res or wc has to be specified")
     wc = 1.22*((2.998e8/freq)/res)/2. # Zen master of the universe (Oleg) says divide by 2
   else: 
       wc = wc[0]

  uvw = tab.getcol("UVW")
  uvdist = np.sqrt(uvw[:,0]**2 + uvw[:,1]**2)
  uvdist[np.where(uvdist==0)] = 1e-3 # avoid division by zero
  info("Calculating taper weights")
  weight_I = bt(uvdist,wc,ws,sign*20)

  if savefig:
    plt.clf()
    plt.plot(uvdist/1e3, weight_I, ".", ms=0.5)
    plt.xlabel('|uv| [km]')
    plt.ylabel('uv-weight')
    plt.ylim(0, 1.05)
    plt.grid()
    plt.xscale("log")
    plt.savefig(savefig)

  weight = np.array([weight_I,weight_I,weight_I,weight_I]).T # use same weights for all four stkes parameters [I,Q,U,V]
  nrows = len(uvw)
  rowchunk = nrows/10
  info("Inserting weights in measurement set")

  for row0 in range(0,nrows,rowchunk):
    nr = min(rowchunk,nrows-row0)
    info("Adding weights to (rows %d to %d)"%(row0,row0+nr-1))
    tab.putcol("WEIGHT",weight[row0:(row0+nr)],row0,nr) # update MS with new weights

  info("Done!")
  tab.close()

def reset_weights(msname):
  tab = table(msname, readonly=False)

  weights = tab.getcol("WEIGHT")
  weights[...] = 1
  nrows = len(weights)
  rowchunk = nrows/10
  info("Reseting weights in \'WEIGHT\' column in MS")

  for row0 in range(0,nrows,rowchunk):
    nr = min(rowchunk,nrows-row0)
    info("Reseting (rows %d to %d)"%(row0,row0+nr-1))
    tab.putcol("WEIGHT",weights[row0:(row0+nr)],row0,nr) # update MS with new weights

  tab.close()
  info("Done!")
