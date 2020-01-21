cwlVersion: v1.1
class: CommandLineTool

requirements:
  DockerRequirement:
    dockerPull: stimela/wsclean:1.2.3
  InlineJavascriptRequirement: {}
  InitialWorkDirRequirement:
    listing:
      - entry: $(inputs.msname)
        writable: true
  InplaceUpdateRequirement:
    inplaceUpdate: true    

baseCommand: wsclean
inputs:
  msname:
    type: Directory
    doc: MS to be imaged. If multiple mses are specified, they need to be phase-rotated
      to the same point on the sky
    inputBinding:
      position: 1
  j:
    type: int?
    doc: Specify number of computing threads to use, i.e., number of cpu cores that
      will be used. None means use all  cores
    inputBinding:
      prefix: -j
  mem:
    type: float?
    doc: Limit memory usage to the given fraction of the total system memory. This
      is an approximate value.
    inputBinding:
      prefix: -mem
  absmem:
    type: float?
    doc: Like 'mem', but this specifies a fixed amount of memory in gigabytes.
    inputBinding:
      prefix: -absmem
  verbose:
    type: boolean?
    doc: Increase verbosity of output
    inputBinding:
      prefix: -verbose
  log_time:
    type: boolean?
    doc: Add date and time to each line in the output.
    inputBinding:
      prefix: -log-time
    default: true
  quite:
    type: boolean?
    doc: Do not output anything but errors.
    inputBinding:
      prefix: -quite
  reorder:
    type: boolean?
    doc: Force or disable reordering of Measurement Set. This can be faster when the
      measurement set needs to be iterated several times, such as with many major
      iterations or in channel imaging mode. If unspecified will only be enabled in
      channel imaging mode
    inputBinding:
      prefix: -reorder
  no_update_model_required:
    type: boolean?
    doc: Save model data in model data column after imaging. It can save time not
      to update the model data column.
    inputBinding:
      prefix: -no-update-model-required
  no_dirty:
    type: boolean?
    doc: Do not save the dirty image
    inputBinding:
      prefix: -no-dirty
  saveweights:
    type: boolean?
    doc: Save the gridded weights in the a fits file named <image-prefix>-weights.fits.
    inputBinding:
      prefix: -saveweights
  apply_primary_beam:
    type: boolean?
    doc: Calculate and apply the primary beam and save images for the Jones components,
      with weighting identical to the weighting as used by the imager. Only available
      for LOFAR.
    inputBinding:
      prefix: -apply-primary-beam
  reuse_primary_beam:
    type: boolean?
    doc: If a primary beam image exists on disk, reuse those images (not implemented
      yet)
    inputBinding:
      prefix: -reuse-primary-beam
  save_uv:
    type: boolean?
    doc: 'Save the gridded uv plane, i.e., the FFT of the residual image. The UV plane
      is complex, hence two images will be output: <prefix>-uv-real.fits and <prefix>-uv-imag.fits'
    inputBinding:
      prefix: -save-uv
  set_differential_lofar_beam:
    type: boolean?
    doc: Assume the visibilities have already been beam-corrected for the reference
      direction.
    inputBinding:
      prefix: -set-differential-lofar-beam
  weight:
    type: string?
    doc: "Weightmode can be: natural, uniform, briggs. Default: uniform. When using\
      \ Briggs' weighting, add the robustness parameter, like: 'weight briggs 0.5'"
    inputBinding:
      prefix: -weight
  super_weight:
    type: float?
    doc: Increase the weight gridding box size, similar to Casa's superuniform weighting
      scheme. The factor can be rational and can be less than one for subpixel weighting.
    inputBinding:
      prefix: -super-weight
  no_mfs_weighting:
    type: boolean?
    doc: In spectral mode, calculate the weights as if the image was made using MFS.
      This makes sure that the sum of channel images equals the MFS weights. Otherwise,
      the channel image will become a bit more naturally weighted. This is only relevant
      for weighting modes that require gridding (i.e., Uniform, Briggs').
    inputBinding:
      prefix: -no-mfs-weighting
  weighting_rank_filter:
    type: float?
    doc: Filter the weights and set high weights to the local mean. The level parameter
      specifies the filter level; any value larger than level*localmean will be set
      to level*localmean.
    inputBinding:
      prefix: -weighting-rank-filter
  weighting_rank_filter_size:
    type: float?
    doc: Set size of weighting rank filter
    inputBinding:
      prefix: -weighting-rank-filter-size
  taper_gaussian:
    type: string?
    doc: Taper the weights with a Gaussian function. This will reduce the contribution
      of long baselines. The beamsize is by default in asec, but a unit can be specified
      as '2amin'
    inputBinding:
      prefix: -taper-gaussian
  taper_tukey:
    type: float?
    doc: Taper the outer weights with a Tukey transition. Lambda specifies the size
      of the transition; use in combination with -maxuv-l.
    inputBinding:
      prefix: -taper-tukey
  taper_inner_tukey:
    type: float?
    doc: aper the weights with a Tukey transition. Lambda specifies the size of the
      transition; use in combination with 'minuv-l'
    inputBinding:
      prefix: -taper-inner-tukey
  taper_edge:
    type: float?
    doc: Taper the weights with a rectangle, to keep a space of lambda between the
      edge and gridded visibilities.
    inputBinding:
      prefix: -taper-edge
  taper_edge_tukey:
    type: float?
    doc: Taper the edge weights with a Tukey window. Lambda is the size of the Tukey
      transition. When 'taper-edge' is also specified, the Tukey transition starts
      inside the inner rectangle.
    inputBinding:
      prefix: -taper-edge-tukey
  size:
    type: int[]?
    doc: Image size in pixels. List of integers (width and height) or a single integer
      for a square image
    inputBinding:
      prefix: -size
  trim:
    type: int[]?
    doc: After inversion, trim the image to the given size.
    inputBinding:
      prefix: -trim
  scale:
    type: string?
    doc: Scale of a pixel. Default unit is arcsec, but can be specificied, e.g. 'scale
      20asec'
    inputBinding:
      prefix: -scale
  continue:
    type: boolean?
    doc: Will continue an earlier WSClean run. Earlier model images will be read and
      model visibilities will be subtracted to create the first dirty residual. CS
      should have been used in the earlier run, and model data should have been written
      to the measurement set for this to work
    inputBinding:
      prefix: -continue
  subtract_model:
    type: boolean?
    doc: Subtract the model from the data column in the first iteration. This can
      be used to reimage an already cleaned image, e.g. at a different resolution.
    inputBinding:
      prefix: -subtract-model
  channels_out:
    type: int?
    doc: Splits the bandwidth and makes count nr. of images
    inputBinding:
      prefix: -channels-out
  nwlayers:
    type: int?
    doc: Use the minimum suggested w-layers for an image of the given size. Can e.g.
      be used to increase accuracy when predicting small part of full image.
    inputBinding:
      prefix: -nwlayers
  nwlayers_for_size:
    type: int[]?
    doc: Use the minimum suggested w-layers for an image of the given size. Can e.g.
      be used to increase accuracy when predicting small part of full image.
    inputBinding:
      prefix: -nwlayers-for-size
  no_small_inversion:
    type: boolean?
    doc: Perform inversion at the Nyquist resolution and upscale the image to the
      requested image size afterwards. This speeds up inversion considerably, but
      makes aliasing slightly worse. This effect is in most cases <1%
    inputBinding:
      prefix: -no-small-inversion
  grid_mode:
    type:
      type: enum
      symbols: [nn, kb, rect]
    doc: ' Kernel and mode used for gridding: kb = Kaiser-Bessel (default with 7 pixels),
      nn = nearest neighbour (no kernel), rect = rectangular window.'
    default: kb
    inputBinding:
      prefix: -grid-mode
  kernel_size:
    type: int?
    doc: Gridding antialiasing kernel size
    inputBinding:
      prefix: -kernel-size
  oversampling:
    type: float?
    doc: Oversampling factor used during gridding
    inputBinding:
      prefix: -oversampling
  make_psf:
    type: boolean?
    doc: Always make the psf, even when no cleaning is performed.
    inputBinding:
      prefix: -make-psf
  make_psf_only:
    type: boolean?
    doc: Only make psf. No other images are made.
    inputBinding:
      prefix: -make-psf-only
  save_gridding:
    type: boolean?
    doc: Save the gridding correction image. This shows the effect of the antialiasing
      filter
    inputBinding:
      prefix: -save-gridding
  dft_prediction:
    type: boolean?
    doc: Predict via a direct Fourier transform. This is slow, but can account for
      direction-dependent effects. This has only effect when 'mgain' is set or 'predict'
      is given.
    inputBinding:
      prefix: -dft-prediction
  dft_with_beam:
    type: boolean?
    doc: Apply the beam during DFT. Currently only works for LOFAR.
    inputBinding:
      prefix: -dft-with-beam
  no_normalize_for_weighting:
    type: boolean?
    doc: "Disable the normalization for the weights, which makes the PSF's peak one.\
      \ See 'visibility-weighting-mode'. Only useful with natural weighting."
    inputBinding:
      prefix: -no-normalize-for-weighting
  baseline_averaging:
    type: int?
    doc: "Enable baseline-dependent averaging. The specified size is in number of wavelengths\
      \ (i.e., uvw-units). One way to calculate this is with <baseline in nr. of lambdas>\
      \ * 2pi * <acceptable integration in s> /(24*60*60)."
    inputBinding:
      prefix: -baseline-averaging
  simulate_noise:
    type: float?
    doc: Will replace every visibility by a Gaussian distributed value with given
      standard deviation before imaging.
    inputBinding:
      prefix: -simulate-noise
  pol:
    type: string?
    doc: "Default: 'I'. Possible values: XX, XY, YX, YY, I, Q, U, V, RR, RL, LR or\
      \ LL (case insensitive). Multiple values can be separated with commas, e.g.:\
      \ 'xx,xy,yx,yy'. Two or four polarizations can be joinedly cleaned (see '-joinpolarizations'),\
      \ but this is not the default. I, Q, U and V polarizations will be directly\
      \ calculated from the visibilities, which is not appropriate for telescopes\
      \ with non-orthogonal feeds, such as MWA and LOFAR. The 'xy' polarization will\
      \ output both a real and an imaginary image, which allows calculating true Stokes\
      \ polarizations for those telescopes."
    inputBinding:
      prefix: -pol
  interval:
    type: int[]?
    doc: Only image the given time interval. Indices specify the timesteps, end index
      is exclusive.
    inputBinding:
      prefix: -interval
  intervals_out:
    type: int?
    doc: Number of intervals to image inside the selected global interval
    inputBinding:
      prefix: -intervals-out
  channel_range:
    type: int[]?
    doc: Only image the given channel range. Indices specify channel indices, end
      index is exclusive
    inputBinding:
      prefix: -channel-range
  field:
    type: int?
    doc: 'Image the given field id. Default: first field (id 0)'
    inputBinding:
      prefix: -field
  spws:
    type: int[]?
    doc: Selects only the spws given in the list. list should be a comma-separated
      list of integers
    inputBinding:
      prefix: -spws
  datacolumn:
    type: string?
    doc: CORRECTED_DATA if it exists, otherwise DATA will be used.
    inputBinding:
      prefix: -data-column
  maxuvw_m:
    type: float?
    doc: Set maximum baseline distance
    inputBinding:
      prefix: -maxuvw-m
  minuvw_m:
    type: float?
    doc: Set minimum baseline distance
    inputBinding:
      prefix: -minuvw-m
  maxuv_l:
    type: float?
    doc: Set maximum uv distance
    inputBinding:
      prefix: -maxuv-l
  minuv_l:
    type: float?
    doc: Set minimum uv distance
    inputBinding:
      prefix: -minuv-l
  niter:
    type: int?
    doc: Maximum number of clean iterations to perform
    inputBinding:
      prefix: -niter
  threshold:
    type: float?
    doc: Stopping clean thresholding in Jy
    inputBinding:
      prefix: -threshold
  auto_threshold:
    type: float?
    doc: Estimate noise level using a robust estimator and stop at sigma x stddev.
    inputBinding:
      prefix: -auto-threshold
  auto_mask:
    type: float?
    doc: Construct a mask from found components and when a threshold of sigma is reached,
      continue cleaning with the mask down to the normal threshold.
    inputBinding:
      prefix: -auto-mask
  local_rms:
    type: boolean?
    doc: Instead of using a single RMS for auto thresholding/masking, use a spatially
      varying RMS image
    inputBinding:
      prefix: -local-rms
  local_rms_window:
    type: int?
    doc: Size of window for creating the RMS background map, in number of PSFs.
    inputBinding:
      prefix: -local-rms-window
  local_rms_method:
    type:
      type: enum
      symbols: [rms, rms-with-min]
    doc: Either 'rms' (default, uses sliding window RMS) or 'rms-with-min' (use max(window
      rms,1.5/5window min))
    default: rms
    inputBinding:
      prefix: -local-rms-method
  gain:
    type: float?
    doc: 'Cleaning gain: Ratio of peak that will be subtracted in each iteration'
    inputBinding:
      prefix: -gain
  mgain:
    type: float?
    doc: 'Cleaning gain for major iterations: Ratio of peak that will be subtracted
      in each major iteration. To use major iterations, 0.85 is a good value.'
    inputBinding:
      prefix: -mgain
  join_polarizations:
    type: boolean?
    doc: Perform cleaning by searching for peaks in the sum of squares of the polarizations,
      but subtract components from the individual images. Only possible when imaging
      two or four Stokes or linear parameters
    inputBinding:
      prefix: -join-polarizations
  join_channels:
    type: boolean?
    doc: Perform cleaning by searching for peaks in the MFS image, but subtract components
      from individual channels. This will turn on mfsweighting by default
    inputBinding:
      prefix: -join-channels
  multiscale:
    type: boolean?
    doc: Clean on different scales. This is a new algorithm. This parameter invokes
      the v1.9 multiscale algorithm, which is slower but more accurate compared to
      the older algorithm, and therefore the recommended one to use. The older algorithm
      is now invoked with 'fast-multiscale'.
    inputBinding:
      prefix: -multiscale
  fast_multiscale:
    type: boolean?
    doc: Clean on different scales. This is a new fast experimental algorithm. This
      method used to be invoked with 'multiscale' before v1.9, but the newer multiscale
    inputBinding:
      prefix: -fast-multiscale
  multiscale_scale_bias:
    type: float?
    doc: Parameter to prevent cleaning small scales in the large-scale iterations.
      A higher bias will give more focus to larger scales
    inputBinding:
      prefix: -multiscale-scale-bias
  multiscale_scales:
    type: int[]?
    doc: 'Sets a list of scales to use in multi-scale cleaning. If unset, WSClean
      will select the delta (zero) scale, scales starting at four times the synthesized
      PSF, and increase by a factor of two until the maximum scale is reached. Example:
      -multiscale-scales 0,5,12.5'
    inputBinding:
      prefix: -multiscale-scales
  iuwt:
    type: boolean?
    doc: Use the IUWT deconvolution algorithm
    inputBinding:
      prefix: -iuwt
  iuwt_snr_test:
    type: boolean?
    doc: Stop IUWT when the SNR decreases. This might help limitting divergence, but
      can occasionally also stop the algorithm too early.
    inputBinding:
      prefix: -iuwt-snr-test
  clean_border:
    type: float?
    doc: Set the border size in which no cleaning is performed, in percentage of the
      width/height of the image. With an image size of 1000 and clean border of 1%,
      each border is 10 pixels.
    inputBinding:
      prefix: -clean-border
  fits_mask:
    type: File?
    doc: Use the specified fits-file as mask during cleaning.
    inputBinding:
      prefix: -fits-mask
  casa_mask:
    type: File?
    doc: Use the specified CASA mask as mask during cleaning.
    inputBinding:
      prefix: -casa-mask
  no_negative:
    type: boolean?
    doc: Do not allow negative components during cleaning
    inputBinding:
      prefix: -no-negative
  stop_negative:
    type: boolean?
    doc: Stop on negative components
    inputBinding:
      prefix: -stop-negative
  fit_spectral_pol:
    type: int?
    doc: Fit a polynomial over frequency to each clean component. This has only effect
      when the channels are joined with 'joinchannels'
    inputBinding:
      prefix: -fit-spectral-pol
  deconvolution_channels:
    type: int?
    doc: Decrease the number of channels as specified by 'channelsout' to the given
      number for deconvolution. Only possible in combination with one of the 'fit-spectral'
      options. Proper residuals/restored images will only be returned when mgain <
      1.
    inputBinding:
      prefix: -deconvolution-channels
  squared_channel_joining:
    type: boolean?
    doc: Use with 'joinchannels' to perform peak finding in the sum of squared values
      over channels, instead of the normal sum. This is useful for imaging QU polarizations
      with non-zero rotation measures, for which the normal sum is insensitive.
    inputBinding:
      prefix: -squared-channel-joining
  force_dynamic_join:
    type: boolean?
    doc: Use alternative joined clean algorithm (feature for testing)
    inputBinding:
      prefix: -force-dynamic-join
  beam_size:
    type: float?
    doc: Set a circular beam size (FWHM) in arcsec for restoring the clean components.
    inputBinding:
      prefix: -beam-size
  beam_shape:
    type: int[]?
    doc: Set the FWHM beam shape for restoring the clean components. Defaults units
      for maj and min are arcsec, and degrees for PA. Can be overriden, e.g. 'beamshape
      1amin 1amin 3deg'. Default is use PSF FWHM sizes
    inputBinding:
      prefix: -beam-shape
  fit_beam:
    type: boolean?
    doc: Determine beam shape by fitting the PSF.
    inputBinding:
      prefix: -fit-beam
  theoretic_beam:
    type: boolean?
    doc: Write the beam in output fits files as calculated from the longest projected
      baseline. This method results in slightly less accurate beam size/integrated
      fluxes, but provides a beam size without making the PSF for quick imaging.
    inputBinding:
      prefix: -theoretic-beam
  no_fit_beam:
    type: boolean?
    doc: Do not determine beam shape from the PSF
    inputBinding:
      prefix: -no-fit-beam
  circular_beam:
    type: boolean?
    doc: Force restoring beam to be circular
    inputBinding:
      prefix: -circular-beam
  elliptical_beam:
    type: boolean?
    doc: Allow restoring beam to be elliptical
    inputBinding:
      prefix: -elliptical-beam
  padding:
    type: float?
    doc: Factor to increase the image size
    inputBinding:
      prefix: -padding
  nmiter:
    type: int?
    doc: Number of major cycles
    inputBinding:
      prefix: -nmiter
  save_source_list:
    type: boolean?
    doc: list of model components from wsclean
    inputBinding:
      prefix: --save-source-list
  predict:
    type: boolean?
    doc: list of model components from wsclean
    inputBinding:
      prefix: --predict
  noise_image:
    type: File?
    doc: Noise image to compute sigma for stopping threshold (in case specified it
      will replace threshold)
    inputBinding:
      prefix: -noise-image
  noise_sigma:
    type: float?
    doc: Noise sigma for stopping deconvolution in the case where noise-image is provided
      (new thresh = sigma*noise_image.std())
    inputBinding:
      prefix: -noise-sigma
  name:
    type: string
    doc: Prefix for output products. Default is prefix 'wsclean'
    inputBinding:
      prefix: -name
  horizontal_mask:
    type: string?
    doc: "Use a mask that avoids cleaning emission beyond the horizon.\
      \ Distance is an angle (e.g. '5deg') that (when positive) decreases\
      \ the size of the mask to stay further away from the horizon"
    inputBinding:
      prefix: -horizontal-mask
  direct_allocation:
    type: string?
    doc: "Enabled direct allocation, which changes memory usage.\
      \ Not recommended for general usage, but when using extremely large images\
      \ that barely fit in memory it might improve memory usage in rare cases"
    inputBinding:
      prefix: -direct-allocation
  parallel_deconvolution:
    type: int?
    doc: Deconvolve subimages in parallel. Subimages will be at most of the given size
    inputBinding:
      prefix: -parallel-deconvolution

outputs:
  source_list:
    type: File
    doc: Output list of model components from wsclean
    outputBinding:
      glob: $(inputs.name)*.txt
  images_out:
    type: File[]
    doc: Output images
    outputBinding:
      glob: $(inputs.name)*.fits
  image_out:
    type: File
    doc: Output image (i.e. <>-image.fits or <>-MFS-image.fits)
    outputBinding:
      glob: ${if (inputs.channels_out) {
                if (inputs.channels_out > 1) {
                  return (inputs.name).concat("*-MFS-image.fits");
                } else {
                  return (inputs.name).concat("*-image.fits");
                }
              } else {
                return (inputs.name).concat("*-image.fits");
              }
             }
  msname_out:
    type: Directory
    doc: Output images
    outputBinding:
      outputEval: $(inputs.msname)
