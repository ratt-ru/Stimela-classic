cwlVersion: v1.1
class: CommandLineTool

requirements:
  EnvVarRequirement:
    envDef:
      USER: root
  DockerRequirement:
    dockerPull: stimela/pybdsf:1.2.0
  InlineJavascriptRequirement: {}
  InitialWorkDirRequirement:
    listing:
      - entry: $(inputs.filename)
  InplaceUpdateRequirement:
    inplaceUpdate: true

baseCommand: python

arguments:
  - prefix: -c
    valueFrom: |
      import bdsf as bdsm  # bdsm it is and bdsm it shall remain

      # JavaScript uses lowercase for bools
      true = True
      false = False
      null = None

      kwargs = ${
        var values = {}; 

        for (var key in inputs) {
            var value = inputs[key];
            if (value) {
              if (value.class == 'Directory') {
                values[key] = value.path;
              } else {
                values[key] = value;
              }
            }
        }
        return values;
      }

      write_opts = {}
      write_catalog = ['bbs_patches', 'bbs_patches_mask',
                       'catalog_type', 'overwrite', 'correct_proj',
                       'format', 'incl_chan', 'incl_empty']
      
      for key, value in kwargs.items():
          if key in write_catalog:
              write_opts[key] = kwargs.pop(key)
      image = kwargs.pop('filename')
      outfile = kwargs.pop('outfile')
      img = bdsm.process_image(image['path'], **kwargs)
      img.write_catalog(outfile=outfile, **write_opts)

inputs:
  outfile:
    type: string
    doc: Prefix for output products.
  split_isl:
    doc: Split island if it is too large, has a large convex deficiency and it opens
      well.
    type: boolean?
  group_by_isl:
    doc: Group all Gaussians in each island into a single source
    type: boolean?
  polarisation_do:
    doc: Find polarisation properties
    type: boolean?
  quiet:
    doc: Suppress text output to screen. Output is still sent to the log file as usual
    type: boolean?
  psf_nsig:
    doc: Kappa for clipping within each bin
    type: float?
  indir:
    doc: Directory of input FITS files. If not set, get from filename
    type: File?
  savefits_normim:
    doc: Save norm image as fits file
    type: boolean?
  rms_map:
    doc: 'Background rms map: True => use 2-D rms map; False => use constant rms;
      None => calculate inside program'
    type: boolean?
  output_all:
    doc: Write out all files automatically to directory 'filename_pybdsm'
    type: boolean?
  rms_box_bright:
    doc: Box size, step size for rms/mean map calculation near bright sources. Specify
      as (box, step) in pixels.
    type: int[]?
  savefits_residim:
    doc: Save residual image as fits file
    type: boolean?
  atrous_bdsm_do:
    doc: Perform source extraction on each wavelet scale
    type: boolean?
  shapelet_basis:
    doc: "Basis set for shapelet decomposition: 'cartesian' or 'polar'. Fair warning\
      \ - polar mode was not implemented at the time of writing this info, use at\
      \ your own risk."
    type: string?
  incl_chan:
    doc: Include flux densities from each channel (if any)?
    type: boolean?
  rms_box:
    doc: Box size, step size for rms/mean map calculation. Specify as (box, step)
      in pixels. E.g., rms_box = (40, 10) => box of 40x40 pixels, step of 10 pixels.
      None => calculate inside program
    type: int[]?
  thresh_isl:
    doc: Threshold for the island boundary in number of sigma above the mean. Determines
      extent of island used for fitting
    type: float?
  spectralindex_do:
    doc: Calculate spectral indices (for multi-channel image)
    type: boolean?
  output_opts:
    doc: Show output options
    type: boolean?
  collapse_wt:
    doc: "Weighting: 'unity' or 'rms'. Average channels with weights = 1 or 1/rms_clip^2\
      \ if collapse_mode = 'average'"
    type: string?
  collapse_ch0:
    doc: Number of the channel for source extraction, if collapse_mode = 'single',
      starting from 0
    type: int?
  incl_empty:
    doc: Include islands without any valid Gaussians (source list only)?
    type: boolean?
  psf_snrcut:
    doc: Minimum SNR for statistics
    type: float?
  beam_spectrum:
    doc: FWHM of synthesized beam per channel. Specify as [(bmaj_ch1, bmin_ch1, bpa_ch1),
      (bmaj_ch2, bmin_ch2, bpa_ch2), etc.] in degrees. E.g., beam_spectrum = [(0.01,
      0.01, 45.0), (0.02,0.01, 34.0)] for two channels. None => all equal to beam
    type: float[]?
  pi_thresh_pix:
    doc: 'Source detection threshold for PI image: threshold for the island peak in
      number of sigma above the mean. Uses thresh_pix if not set.'
    type: float?
  splitisl_maxsize:
    doc: If island size in beam area is more than this, consider splitting island.
      Min value is 50
    type: float?
  specind_maxchan:
    doc: Maximum number of channels to average for a given source when when attempting
      to meet target SNR. 1 => no averaging; 0 => no maximum
    type: int?
  ini_gausfit:
    doc: "Initial guess for Gaussian parameters: 'default', 'simple', or 'nobeam'"
    type:
      type: enum
      symbols: [default, simple, nobeam]
    default: default
  do_mc_errors:
    doc: stimate uncertainties for 'M'-type sources using Monte Carlo method
    type: boolean?
  pi_thresh_isl:
    doc: Threshold for PI island boundary in number of sigma above the mean. Uses
      thresh_isl if not set.
    type: float?
  flag_maxsize_fwhm:
    doc: Flag Gaussian if fwhm-contour times factor extends beyond island
    type: float?
  beam_sp_derive:
    doc: If True and beam_spectrum is None, then assume header beam is for median
      frequency and scales with frequency for channels
    type: boolean?
  ncores:
    doc: Number of cores to use during fitting, None => use all
    type: int?
  shapelet_fitmode:
    doc: "Calculate shapelet coeff's by fitting ('fit') or integrating (None). WARNING:\
      \ the default is 'fit', not none, so to run in default mode, explicitely set\
      \ this to 'fit', else leave as is."
    type: string?
  print_timing:
    doc: Print basic timing information
    type: boolean?
  fdr_alpha:
    doc: Alpha for FDR algorithm for thresholds
    type: float?
  fdr_ratio:
    doc: "For thresh = None; if #false_pix / #source_pix < fdr_ratio, thresh = 'hard'\
      \ else thresh = 'fdr'"
    type: float?
  flag_smallsrc:
    doc: Flag sources smaller than flag_minsize_bm times beam area
    type: boolean?
  psf_snrtop:
    doc: Fraction of SNR > snrcut as primary generators
    type: float?
  psf_vary_do:
    doc: Calculate PSF variation across image
    type: boolean?
  verbose_fitting:
    doc: Print out extra information during fitting
    type: boolean?
  savefits_rmsim:
    doc: Save background rms image as fits file
    type: boolean?
  ini_method:
    doc: "Method by which inital guess for fitting of Gaussians is chosen: 'intensity'\
      \ or 'curvature'"
    type:
      type: enum
      symbols: [intensity, curvature]
    default: intensity
  thresh:
    doc: "Type of thresholding: None => calculate inside program, 'fdr' => use false\
      \ detection rate algorithm, 'hard' => use sigma clipping"
    type:
      - 'null'
      - type: enum
        symbols: [fdr, hard]
  rms_value:
    doc: Value of constant rms in Jy/beam to use if rms_map = False. None => calculate
      inside program
    type: float?
  atrous_sum:
    doc: Fit to the sum of remaining wavelet scales
    type: boolean?
  flag_maxsize_isl:
    doc: Flag Gaussian if x, y bounding box around sigma-contour is factor times island
      bbox
    type: float?
  flagchan_rms:
    doc: Flag channels before (averaging and) extracting spectral index, if their
      rms is more than 5 (clipped) sigma outside the median rms over all channels,
      but only if <= 10% of channels
    type: boolean?
  atrous_orig_isl:
    doc: Restrict wavelet Gaussians to islands found in original image
    type: boolean?
  group_method:
    doc: Group Gaussians into sources using 'intensity' map or 'curvature' map
    type:
      type: enum
      symbols: [intensity, curvature]
    default: intensity
  src_radius_pix:
    doc: Radius of the island (if src_ra_dec is not None) in pixels. None => radius
      is set to the FWHM of the beam major axis.
    type: int?
  detection_image:
    doc: Detection image file name used only for detecting islands of emission. Source
      measurement is still done on the main image
    type: File?
  correct_proj:
    doc: Correct source parameters for image projection (BBS format only)?
    type: boolean?
  bbs_patches:
    doc: "BBS format, type of patch to use: None => no patches. 'single' => all Gaussians\
      \ in one patch. 'gaussian' => each Gaussian gets its own patch. 'source' =>\
      \ all Gaussians belonging to a single source are grouped into one patch. 'mask'\
      \ => use mask file specified by bbs_patches_mask"
    type:
      type: enum
      symbols: [single, gaussian, source, mask]
    default: source
  psf_itess_method:
    doc: 0 = normal, 1 = 0 + round, 2 = LogSNR, 3 =SqrtLogSNR
    type: int?
  flag_maxsize_bm:
    doc: Flag Gaussian if area greater than flag_maxsize_bm times beam area
    type: float?
  peak_maxsize:
    doc: If island size in beam area is more than this, attempt to fit peaks iteratively
      (if peak_fit = True). Min value is 30
    type: float?
  frequency:
    doc: Frequency in Hz of input image. E.g., frequency = 74e6. None => get from
      header.
    type: float?
  frequency_sp:
    doc: Frequency in Hz of channels in input image when more than one channel is
      present. E.g., frequency_sp = [74e6, 153e6]. None => get from header
    type: float[]?
  flagchan_snr:
    doc: Flag channels that do not meet SNR criterion set by specind_snr
    type: boolean?
  group_tol:
    doc: 'Tolerance for grouping of Gaussians into sources: larger values will result
      in larger sources'
    type: float?
  do_cache:
    doc: Cache internally derived images to disk
    type: boolean?
  adaptive_rms_box:
    doc: Use adaptive rms_box when determining rms and mean maps
    type: boolean?
  psf_smooth:
    doc: Size of Gaussian to use for smoothing of interpolated images in arcsec. If
      not set, no smoothing.
    type: float?
  shapelet_do:
    doc: Decompose islands into shapelets
    type: boolean?
  atrous_lpf:
    doc: Low pass filter, either 'b3' or 'tr', for B3 spline or Triangle
    type:
      type: enum
      symbols: [b3, tr]
    default: b3
  fittedimage_clip:
    doc: Sigma for clipping Gaussians while creating fitted image
    type: float?
  spline_rank:
    doc: Rank of the interpolating function for rms/mean map
    type: int?
  flagging_opts:
    doc: Show options for Gaussian flagging
    type: boolean?
  flag_minsnr:
    doc: Flag Gaussian if peak is less than flag_minsnr times thresh_pix times local
      rms
    type: float?
  psf_stype_only:
    doc: "Restrict sources to be only of type 'S' "
    type: boolean?
  psf_snrcutstack:
    doc: Unresolved sources with higher SNR taken for stacked psfs
    type: float?
  fix_to_beam:
    doc: Fix major and minor axes and PA of Gaussians to beam?
    type: boolean?
  bbs_patches_mask:
    doc: "Name of the mask file (of same size as input image) that defines the patches\
      \ if bbs_patches = 'mask'"
    type: File?
  pi_fit:
    doc: Check the polarized intesity (PI) image for sources not found in Stokes I
    type: boolean?
  kappa_clip:
    doc: Kappa for clipped mean and rms. None => calculate inside program
    type: float?
  solnname:
    doc: Name of the run, to be prepended to the name of the output directory. E.g.,
      solname='Run_1'
    type: string?
  thresh_pix:
    doc: 'Source detection threshold: threshold for the island peak in number of sigma
      above the mean. If false detection rate thresholding is used, this value is
      ignored and thresh_pix is calculated inside the program'
    type: float?
  peak_fit:
    doc: Find and fit peaks of large islands iteratively
    type: boolean?
  psf_over:
    doc: Factor of nyquist sample for binning bmaj, etc. vs SNR
    type: int?
  catalog_type:
    doc: "Type of catalog to write:  'gaul' - Gaussian list, 'srl' - source list (formed\
      \ by grouping Gaussians), 'shap' - shapelet list (FITS format only)"
    type:
      type: enum
      symbols: [srl, gaul, shap]
    default: srl
  aperture:
    doc: Radius of aperture in pixels inside which aperture fluxes are measured for
      each source. None => no aperture fluxes measured
    type: boolean?
  use_scipy_fft:
    doc: Use fast SciPy FFT for convolution
    type: boolean?
  savefits_rankim:
    doc: Save island rank image as fits file
    type: boolean?
  specind_snr:
    doc: Target SNR to use when fitting power law. If there is insufficient SNR, neighboring
      channels are averaged to attempt to obtain the target SNR. Channels with SNRs
      below this will be flagged if flagchan_snr = True
    type: float?
  minpix_isl:
    doc: Minimum number of pixels with emission per island (minimum is 6 pixels).
      None -> calculate inside program
    type: int?
  check_outsideuniv:
    doc: Check for pixels outside the universe
    type: boolean?
  bmpersrc_th:
    doc: Theoretical estimate of number of beams per source. None => calculate inside
      program
    type: float?
  atrous_jmax:
    doc: Max allowed wavelength order, 0 => calculate inside program
    type: int?
  collapse_av:
    doc: List of channels to average if collapse_mode = 'average', starting from 0.
      E.g., collapse_av = [0, 1, 5]. [] => all
    type: int[]?
  flag_minsize_bm:
    doc: Flag Gaussian if peak is greater than flag_maxsnr times image value at the
      peak
    type: float?
  format:
    doc: Format of output catalog
    type:
      type: enum
      symbols: [bbs, ds9, fits, star, kvis, ascii, csv, casabox, sagecal]
    default: fits
  psf_fwhm:
    doc: FWHM of the PSF. Specify as (maj, min, pos ang E of N) in degrees. E.g.,
      psf_fwhm = (0.06, 0.02, 13.3). Estimates from the image if not set
    type: float[]?
  shapelet_gresid:
    doc: Use Gaussian residual image for shapelet decomposition?
    type: boolean?
  stop_at:
    doc: "Stops after: 'isl' = island finding step or 'read' = image reading step"
    type:
      - 'null'
      - type: enum
        symbols: [isl, read]
  filename:
    doc: Input image file name
    type: File
  beam:
    doc: FWHM of restoring beam. Specify as (maj, min, pos ang E of N) in degrees.
      E.g., beam = (0.06, 0.02, 13.3). None => get from header
    type: float[]?
  overwrite:
    doc: Overwrite existing file?
    type: boolean?
  atrous_do:
    doc: Decompose Gaussian residual image into multiple scales
    type: boolean?
  collapse_mode:
    doc: "Collapse method: 'average' or 'single'. Average channels or take single\
      \ channel to perform source detection on"
    type:
      type: enum
      symbols: [average, single]
    default: average
  flag_maxsnr:
    doc: Flag Gaussian if peak is greater than flag_maxsnr times image value at the
      peak
    type: float?
  savefits_meanim:
    doc: Save background mean image as fits file
    type: boolean?
  psf_kappa2:
    doc: Kappa for clipping for analytic fit
    type: float?
  psf_high_snr:
    doc: SNR above which all sources are taken to be unresolved. E.g., psf_high_snr
      = 20.0. If unset, no such selection is made
    type: float?
  blank_limit:
    doc: Limit in Jy/beam below which pixels are blanked. None => no such blanking
      is done
    type: float?
  aperture_posn:
    doc: "Position the aperture (if aperture is not None) on: 'centroid' or 'peak' of the source"
    type:
      type: enum
      symbols: [centroid, peak]
    default: centroid
  flag_bordersize:
    doc: Flag Gaussian if centre is outside border - flag_bordersize pixels
    type: int?
  trim_box:
    doc: "Do source detection on only a part of the image.\
      \ Specify as (xmin, xmax, ymin, ymax) in pixels.\
      \ E.g., trim_box = (120, 840, 15, 895). None => use entire image"
    type: int[]?
  mean_map:
    doc: "Background mean map: 'default' => calc whether to use or not, 'zero' =>\
      \ 0, 'const' => clipped mean, 'map' => use 2-D map"
    type:
      type: enum
      symbols: [default, zero, const, map]
    default: default
  src_ra_dec:
    doc: "List of source positions at which fitting is done.\
      \ E.g., src_ra_dec = [(197.1932, 47.9188), (196.5573, 42.4852)]"
    type: string[]?
  opdir_overwrite:
    doc: "'overwrite'/'append': If output_all=True, delete existing files or append\
      \ a new directory"
    type: string?
  adaptive_thresh:
    doc: "Sources with pixels above adaptive_thresh*clipped_rms will be considered\
      \ as bright sources. Minimum is 10.0."
    type: float?

outputs:
  model_out:
    type: File
    doc: "Output file name. None => file is named automatically; 'SAMP' => send\\ to\
      \ SAMP hub (e.g., to TOPCAT, ds9, or Aladin)"
    outputBinding:
      glob: $(inputs.outfile)
  models_out:
    type: File[]
    doc: "Output files name. i.e To pass to a tool that requires models in a list format"
    outputBinding:
      glob: $(inputs.outfile)
