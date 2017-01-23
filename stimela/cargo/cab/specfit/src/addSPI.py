#!/usr/bin/env python
import pyfits
import numpy as np
import Tigger
import sys,os
from astLib.astWCS import WCS

def fitsInfo(fitsname = None):
    """
    Get fits info
    """
    hdu = pyfits.open(fitsname)
    hdr = hdu[0].header
    ra = hdr['CRVAL1']
    dra = abs(hdr['CDELT1'])
    raPix = hdr['CRPIX1']
    dec = hdr['CRVAL2']
    ddec = abs(hdr['CDELT2'])
    decPix = hdr['CRPIX2']
    freq0 = 0
    for i in range(1,hdr['NAXIS']+1):
        if hdr['CTYPE%d'%i].strip() == 'FREQ':
            freq0 = hdr['CRVAL%d'%i]
            break

    ndim = hdr["NAXIS"]
    imslice = np.zeros(ndim, dtype=int).tolist()
    imslice[-2:] = slice(None), slice(None)
    
    image = hdu[0].data[imslice]
    wcs = WCS(hdr,mode='pyfits')

    return {'image':image,'wcs':wcs,'ra':ra,'dec':dec,'dra':dra,'ddec':ddec,'raPix':raPix,'decPix':decPix,'freq0':freq0}

def sky2px(wcs,ra,dec,dra,ddec,cell):
    """convert a sky region to pixel positions"""
    beam =  3.971344894833e-03 # beam size, 
    dra = beam if dra<beam else dra # assume every source is at least as large as the psf
    ddec = beam if ddec<beam else ddec
    offsetDec = (ddec/2.)/cell
    offsetRA = (dra/2.)/cell 
    raPix,decPix = wcs.wcs2pix(ra,dec)
    return np.array([int(raPix-offsetRA),int(raPix+offsetRA),int(decPix-offsetDec),int(decPix+offsetDec)])

def RemoveSourcesWithoutSPI(lsmname_in, lsmname_out):
    model = Tigger.load(lsmname_in) 
    sources = [src for src in model.sources]    
    for src in sources:
        if not src.spectrum:
            model.sources.remove(src)
    model.save(lsmname_out)

def CombineSourcesInCluster(lsmname_in, lsmname_out):
    model = Tigger.load(lsmname_in)
    for src in model.sources:
        if src.cluster_size>1 and rad2arcsec(src.r)>30:
            cluster_sources = [src1 for src1 in model.sources if src1.cluster is src.cluster]
            flux_sources = [src1.flux.I for src1 in cluster_sources]
            max_flux_index = flux_sources.index(max( flux_sources))
            cluster_sources[max_flux_index].flux.I = sum([src1.flux.I for src1 in cluster_sources])
        for src2 in cluster_sources:
            if src2 is not cluster_sources[max_flux_index]:
                model.sources.remove(src2) 
        cluster_sources[max_flux_index].cluster_size=1
    model.save(lsmname_out)

def rad2arcsec(x):
    return x*3600.0*180.0/np.pi


def addSPI(fitsname_alpha=None, fitsname_alpha_error=None, lsmname=None, outfile=None, freq0=None, spitol=(-10,10)):
    """
        Add spectral index to a tigger lsm from a spectral index map (fits format)
        takes in a spectral index map, input lsm and output lsm name.
    """
#    import pylab as plt
    print "INFO: Getting fits info from: %s, %s" %(fitsname_alpha, fitsname_alpha_error)

    fits_alpha = fitsInfo(fitsname_alpha)    # Get fits info
    image_alpha = fits_alpha['image']     # get image data

    if fitsname_alpha_error:   
        fits_alpha_error = fitsInfo(fitsname_alpha_error)
        image_alpha_error = fits_alpha_error['image']
    else:
        fits_alpha_error = fitsInfo(fitsname_alpha)
        image_alpha_error = fits_alpha_error['image']
        image_alpha_error[...] = 1.0

    # may supply FITS file for freq0, in which case just pull ref frequency from FITS file,
    # else explicit frequency, else get frequency from alpha image
    if type(freq0) is str:
        freq0 = fitsInfo(freq0)['freq0']
    else:
        freq0 = freq0 or fits_alpha['freq0']

    model = Tigger.load(lsmname)    # load sky model
    rad = lambda a: a*(180/np.pi) # convert radians to degrees

    for src in model.sources: 
        ra = rad(src.pos.ra)
        dec = rad(src.pos.dec)
        tol = 30./3600. # Tolerance, only add SPIs to sources outside this tolerance (radial distance from centre)
        beam =  3.971344894833e-03 # psf size, assume all sources are at least as large as the psf

        if np.sqrt((ra-fits_alpha["ra"])**2 + (dec-fits_alpha["dec"])**2)>tol: # exclude sources within {tol} of phase centre
            dra = rad(src.shape.ex) if src.shape  else beam # cater for point sources
            ddec = rad(src.shape.ex) if src.shape  else beam # assume source extent equal to the Gaussian major axis along both ra and dec axes
            rgn = sky2px(fits_alpha["wcs"],ra,dec,dra,ddec,fits_alpha["dra"]) # Determine region of interest

            imslice = slice(rgn[2], rgn[3]), slice(rgn[0], rgn[3])
            alpha = image_alpha[imslice]
            alpha_error = image_alpha_error[imslice]
            good = np.where( np.logical_and(alpha!=0, alpha!=np.nan))
            alpha = alpha[good]
            alpha_error = alpha_error[good]
            good = np.where( np.logical_and(alpha_error!=np.nan, alpha_error!=np.inf))

            alpha = alpha[good]
            alpha_error = alpha_error[good]

            subIm_weight = 1/alpha_error
            subIm_weighted = alpha*subIm_weight

            if len(subIm_weighted)>0:
                subIm_normalization = np.sum(subIm_weight)

                spi = float(np.sum(subIm_weighted)/subIm_normalization)
                if spi > spitol[0] or spi < spitol[-1]:
                    print "INFO: Adding spi: %.3f (at %.3g MHz) to source %s"%(spi, freq0/1e6, src.name)
                    src.spectrum = Tigger.Models.ModelClasses.SpectralIndex(spi, freq0)
            else:
                print "ALERT: no spi info found in %s for source %s"%(fitsname_alpha, src.name)

    model.save(outfile)

if __name__=="__main__":
    fitsname_alpha = sys.argv[1]
    #fitsname_alpha_error = sys.argv[2]
    lsmname = sys.argv[2]
    outfile = sys.argv[3]
    addSPI(fitsname_alpha, None, lsmname, outfile) 
