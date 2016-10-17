#!/usr/bin/env python
import os
import sys
import pyfits
import numpy as np
import math
from scipy.optimize import leastsq

N1 = 0.682689492137 # one stadard dev from mean
def mad(data,sigma_level):
    sigma = np.median(abs(data)) / N1
    return sigma_level * sigma

def fit_func(freqs,freq0,a=0,b=0):
    """ Spectral line fitting function"""
    lfr = freqs/freq0
    return lfr**(a + b*np.log(lfr))

def get_spec(fitsname,spi=True,spc=False,sp2=False,start=0,end=0,
             sigma_level=10,outname_spi=None,outname_spc=None):
    """ Get spectral line info """
    hdu = pyfits.open(fitsname)[0]
    data = hdu.data
    hdr = hdu.header

    # Get frequency info
    def freqInfo(hdr):
        naxis = hdr['NAXIS']
        for axis in range(1,naxis+1):
            if hdr['CTYPE%d'%axis].upper().startswith('FREQ'):
                nchan = hdr['NAXIS%d'%axis]
                dfreq = hdr['CDELT%d'%axis]
                freq0 = hdr['CRVAL%d'%axis]
                ind = hdr['CRPIX%d'%axis]
                cnt_freq = freq0 + (nchan/2 - ind) * dfreq
                axis = naxis - axis
                return naxis,axis,nchan,dfreq,cnt_freq

    naxis,freq_axis,nchan,dfreq,freq0 = freqInfo(hdr)
    imdata = [0]*naxis

    if end<0:
        end = nchan + end
    else: 
        start = start or 0
        end = end or nchan-1
    width = end + 1 -start    
    imdata[freq_axis] = np.arange(start,width,1)
    imdata[-2:] = [slice(None)]*2 # assume image data is NAXIS{1,2} in fits file

    # Define structure for spectral maps 
    shape = [2]+list(data.shape)[-2:]
    spi_map = np.zeros(shape,dtype=float)

    if spc:
        spc_map = np.zeros(shape,dtype=float)

    mfs = data[imdata].sum(0)/(width) # average map over frequency
    thresh = mad(mfs,sigma_level) * math.sqrt(width) # Noise in each channel ~sqrt(bandwith/channel width)

    hdr['CRVAL%d'%abs(freq_axis-naxis)] = freq0# Update fits header for MFS map header
    # Save mfs image
    pyfits.writeto(fitsname.replace('.fits','-MFS.fits'),data.sum(freq_axis)/(width),hdr,clobber=True)

    ind = np.where(mfs>thresh) # find pixels with values above threshold
    
    bw = dfreq*(end-start) # 
    freq = np.linspace(freq0-bw/2,freq0+bw/2,width)
    import pylab as plt
    for x,y in np.array(ind).T:
        imdata[-2:] = x,y
        spec_line = data[imdata] # get spectral line
#        spec_line = spec_line/max(spec_line) # Normalize
#        plt.plot(freq,spec_line,'kx')

        if spc: 
            func = lambda freq,freq0,a,b: (freq/freq0)**(a + np.log(freq/freq0)*b)
            x0 = freq0,-0.7,0
        else: 
            func = lambda freq,freq0,a: (freq/freq0)**a
            x0 = freq0,-0.7

        residual = lambda params,freq,data: data - func(freq,*params) 
        parms = leastsq(residual,x0,args=(freq,spec_line),full_output=1,ftol=1e-12,xtol=1e-12,col_deriv=True)
        if parms[1] is not None:
         # Calculate covariance and error of fit
            cov = (residual(parms[0],freq,spec_line)**2).sum()/(end-start-len(x0)) * parms[1]
            err = np.sqrt(np.diag(cov))
        else : 
            err = [np.nan]*3
            
        spi_map[0,x,y] = parms[0][1]
        spi_map[1,x,y] = err[1]
        if spc: 
            spc_map[0,x,y] = parms[0][2]
            spc_map[1,x,y] = err[2]
        
#        plt.plot(freq,func(freq,*parms[0]),'r-')
#        plt.show()
#        print '\n%.4g +/- %.4g, %.2e +/- %.2e, %.2f +/- %.2e'%(parms[0][0],err[0],
#                                                           parms[0][1],err[1],
#                                                           parms[0][2],err[2]
#)
    def adwcs(fromhdr,tohdr):
        """ transfer wcs info """
        for key,val in fromhdr.iteritems():
           if key in 'CTYPE1 CTYPE2 CRVAL1 CRVAL2 CDELT1 CDELT2 CRPIX1 CRPIX2 CUNIT1 CUNIT2'.split():
              tohdr[key] = val
           
    spi_hdr = dict(CTYPE3='SPI',CRVAL3=1,CDELT3=1,CUNIT3='UNIT --- (nu/n0)^spi',
)
    adwcs(hdr,spi_hdr)
    makefits(outname_spi or fitsname.replace('.fits','-spi.fits'),spi_map,spi_hdr)
    # make spectral curvature map
    if spc:
        spc_hdr = dict(CTYPE3='SPC',CRVAL3=1,CDELT3=1,CUNIT3='UNIT',
)
        adwcs(hdr,spc_hdr)
        makefits(outname_spc or fitsname.replace('.fits','-spc.fits'),spc_map,spc_hdr)

def makefits(fitsname,data,hdr_info):
    """ create fits file """
    hdr = pyfits.Header()
    for key,val in hdr_info.iteritems():
        hdr[key] = val
    pyfits.writeto(fitsname,data,hdr,clobber=True)
    

if __name__=='__main__':
    get_spec(sys.argv[1],start=0,spc=False,sigma_level=20)
