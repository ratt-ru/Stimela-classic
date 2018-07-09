## Auto generated cwl file
cwlVersion: v1.0
class: CommandLineTool

requirements:
  - class: DockerRequirement
    dockerPull: sphemakh/den
  - class: InlineJavascriptRequirement
  - class: InitialWorkDirRequirement
    listing:
    - entry: $(inputs.ms)
      writable: true

baseCommand: /usr/bin/wsclean

arguments:
  - -no-update-model-required
  - -size 
  - $(inputs.size)
  - $(inputs.size)

inputs:
  name:
    type: string
    doc: "Prefix for output products. Default is prefix of MS"
    inputBinding:
      prefix: -name
      position: 2
  threads:
    type: int?
    doc: "Specify number of computing threads to use, i.e., number of cpu cores that will be used. None means use all  cores"
    inputBinding:
      prefix: -threads
      position: 3
  mem:
    type: float?
    doc: "Limit memory usage to the given fraction of the total system memory. This is an approximate value."
    inputBinding:
      prefix: -mem
      position: 4
  absmem:
    type: float?
    doc: "Like 'mem', but this specifies a fixed amount of memory in gigabytes."
    inputBinding:
      prefix: -absmem
      position: 5
  verbose:
    type: boolean?
    doc: "Increase verbosity of output"
    inputBinding:
      prefix: -verbose
      position: 6
  log-time:
    type: boolean?
    doc: "Add date and time to each line in the output."
    inputBinding:
      prefix: -log-time
      position: 7
  quite:
    type: boolean?
    doc: "Do not output anything but errors."
    inputBinding:
      prefix: -quite
      position: 8
  reorder:
    type: boolean?
    doc: "Force or disable reordering of Measurement Set. This can be faster when the measurement set needs to be iterated several times, such as with many major iterations or in channel imaging mode. If unspecified will only be enabled in channel imaging mode"
    inputBinding:
      prefix: -reorder
      position: 9
  no-update-model-required:
    type: boolean?
    doc: "Save model data in model data column after imaging. It can save time not to update the model data column."
    inputBinding:
      prefix: -no-update-model-required
      position: 10
  no-dirty:
    type: boolean?
    doc: "Do not save the dirty image"
    inputBinding:
      prefix: -no-dirty
      position: 11
  saveweights:
    type: boolean?
    doc: "Save the gridded weights in the a fits file named <image-prefix>-weights.fits."
    inputBinding:
      prefix: -saveweights
      position: 12
  apply-primary-beam:
    type: boolean?
    doc: "Calculate and apply the primary beam and save images for the Jones components, with weighting identical to the weighting as used by the imager. Only available for LOFAR."
    inputBinding:
      prefix: -apply-primary-beam
      position: 13
  reuse-primary-beam:
    type: boolean?
    doc: "If a primary beam image exists on disk, reuse those images (not implemented yet)"
    inputBinding:
      prefix: -reuse-primary-beam
      position: 14
  saveuv:
    type: boolean?
    doc: "Save the gridded uv plane, i.e., the FFT of the residual image. The UV plane is complex, hence two images will be output: <prefix>-uv-real.fits and <prefix>-uv-imag.fits"
    inputBinding:
      prefix: -saveuv
      position: 15
  set-differential-lofar-beam:
    type: boolean?
    doc: "Assume the visibilities have already been beam-corrected for the reference direction."
    inputBinding:
      prefix: -set-differential-lofar-beam
      position: 16
  weight:
    type: string[]?
    doc: "Weightmode can be: natural, uniform, briggs. Default: uniform. When using Briggs' weighting, add the robustness parameter, like: 'weight briggs 0.5'"
    inputBinding:
      prefix: -weight
      separate: true
      position: 17
  superweight:
    type: float?
    doc: "Increase the weight gridding box size, similar to Casa's superuniform weighting scheme. The factor can be rational and can be less than one for subpixel weighting."
    inputBinding:
      prefix: -superweight
      position: 18
  nomfsweighting:
    type: boolean?
    doc: "In spectral mode, calculate the weights as if the image was made using MFS. This makes sure that the sum of channel images equals the MFS weights. Otherwise, the channel image will become a bit more naturally weighted. This is only relevant for weighting modes that require gridding (i.e., Uniform, Briggs')."
    inputBinding:
      prefix: -nomfsweighting
      position: 19
  weighting-rank-filter:
    type: float?
    doc: "Filter the weights and set high weights to the local mean. The level parameter specifies the filter level; any value larger than level*localmean will be set to level*localmean."
    inputBinding:
      prefix: -weighting-rank-filter
      position: 20
  weighting-rank-filter-size:
    type: float?
    doc: "Set size of weighting rank filter"
    inputBinding:
      prefix: -weighting-rank-filter-size
      position: 21
  taper-gaussian:
    type: string?
    doc: "Taper the weights with a Gaussian function. This will reduce the contribution of long baselines. The beamsize is by default in asec, but a unit can be specified as '2amin'"
    inputBinding:
      prefix: -taper-gaussian
      position: 22
  taper-tukey:
    type: float?
    doc: "Taper the outer weights with a Tukey transition. Lambda specifies the size of the transition; use in combination with -maxuv-l."
    inputBinding:
      prefix: -taper-tukey
      position: 23
  taper-inner-tukey:
    type: float?
    doc: "aper the weights with a Tukey transition. Lambda specifies the size of the transition; use in combination with 'minuv-l'"
    inputBinding:
      prefix: -taper-inner-tukey
      position: 24
  taper-edge:
    type: float?
    doc: "Taper the weights with a rectangle, to keep a space of lambda between the edge and gridded visibilities."
    inputBinding:
      prefix: -taper-edge
      position: 25
  taper-edge-tukey:
    type: float?
    doc: "Taper the edge weights with a Tukey window. Lambda is the size of the Tukey transition. When 'taper-edge' is also specified, the Tukey transition starts inside the inner rectangle."
    inputBinding:
      prefix: -taper-edge-tukey
      position: 26
  size:
    type: int?
    doc: "Image size in pixels. List of integers (width and height) or a single integer for a square image"
    default: 512
  scale:
    type: string?
    default: 1asec
    doc: "Scale of a pixel. Default unit is arcsec, but can be specificied, e.g. 'scale 20asec'"
    inputBinding:
      prefix: -scale
      position: 29
  continue:
    type: boolean?
    doc: "Will continue an earlier WSClean run. Earlier model images will be read and model visibilities will be subtracted to create the first dirty residual. CS should have been used in the earlier run, and model data should have been written to the measurement set for this to work"
    inputBinding:
      prefix: -continue
      position: 30
  subtract-model:
    type: boolean?
    doc: "Subtract the model from the data column in the first iteration. This can be used to reimage an already cleaned image, e.g. at a different resolution."
    inputBinding:
      prefix: -subtract-model
      position: 31
  channels-out:
    type: int?
    doc: "Splits the bandwidth and makes count nr. of images"
    inputBinding:
      prefix: -channelsout
      position: 32
  nwlayers:
    type: int?
    doc: "Use the minimum suggested w-layers for an image of the given size. Can e.g. be used to increase accuracy when predicting small part of full image."
    inputBinding:
      prefix: -nwlayers
      position: 33
  nwlayers-for-size:
    type: int[]?
    doc: "Use the minimum suggested w-layers for an image of the given size. Can e.g. be used to increase accuracy when predicting small part of full image."
    inputBinding:
      prefix: -nwlayers-for-size
      separate: true
      position: 34
  nosmallinversion:
    type: boolean?
    doc: "Perform inversion at the Nyquist resolution and upscale the image to the requested image size afterwards. This speeds up inversion considerably, but makes aliasing slightly worse. This effect is in most cases <1%"
    inputBinding:
      prefix: -nosmallinversion
      position: 35
  make-psf:
    type: boolean?
    doc: "Always make the psf, even when no cleaning is performed."
    inputBinding:
      prefix: -make-psf
      position: 39
  make-psf-only:
    type: boolean?
    doc: "Only make psf. No other images are made."
    inputBinding:
      prefix: -make-psf-only
      position: 40
  savegridding:
    type: boolean?
    doc: "Save the gridding correction image. This shows the effect of the antialiasing filter"
    inputBinding:
      prefix: -savegridding
      position: 41
  dft-prediction:
    type: boolean?
    doc: "Predict via a direct Fourier transform. This is slow, but can account for direction-dependent effects. This has only effect when 'mgain' is set or 'predict' is given."
    inputBinding:
      prefix: -dft-prediction
      position: 42
  dft-with-beam:
    type: boolean?
    doc: "Apply the beam during DFT. Currently only works for LOFAR."
    inputBinding:
      prefix: -dft-with-beam
      position: 43
    inputBinding:
      prefix: -visibility-weighting-mode
      position: 44
  no-normalize-for-weighting:
    type: boolean?
    doc: "Disable the normalization for the weights, which makes the PSF's peak one. See 'visibility-weighting-mode'. Only useful with natural weighting."
    inputBinding:
      prefix: -no-normalize-for-weighting
      position: 45
  baseline-averaging:
    type: int?
    doc: "Enable baseline-dependent averaging. The specified size is in number of wavelengths (i.e., uvw-units). One way to calculate this is with <baseline in nr. of lambdas> * 2pi * <acceptable integration in s> /(24*60*60)."
    inputBinding:
      prefix: -baseline-averaging
      position: 46
  simulate-noise:
    type: float?
    doc: "Will replace every visibility by a Gaussian distributed value with given standard deviation before imaging."
    inputBinding:
      prefix: -simulate-noise
      position: 47
  pol:
    type: string?
    default: I
    doc: "Default: 'I'. Possible values: XX, XY, YX, YY, I, Q, U, V, RR, RL, LR or LL (case insensitive). Multiple values can be separated with commas, e.g.: 'xx,xy,yx,yy'. Two or four polarizations can be joinedly cleaned (see '-joinpolarizations'), but this is not the default. I, Q, U and V polarizations will be directly calculated from the visibilities, which is not appropriate for telescopes with non-orthogonal feeds, such as MWA and LOFAR. The 'xy' polarization will output both a real and an imaginary image, which allows calculating true Stokes polarizations for those telescopes."
    inputBinding:
      prefix: -pol
      position: 48
  interval:
    type: int[]?
    doc: "Only image the given time interval. Indices specify the timesteps, end index is exclusive."
    inputBinding:
      prefix: -interval
      separate: true
      position: 49
  intervals-out:
    type: int?
    doc: "Number of intervals to image inside the selected global interval"
    inputBinding:
      prefix: -intervalsout
      position: 50
  channel-range:
    type: int[]?
    doc: "Only image the given channel range. Indices specify channel indices, end index is exclusive"
    inputBinding:
      prefix: -channelrange
      separate: true
      position: 51
  field:
    type: int?
    doc: "Image the given field id. Default: first field (id 0)"
    inputBinding:
      prefix: -field
      position: 52
  spws:
    type: int[]?
    doc: "Selects only the spws given in the list. list should be a comma-separated list of integers"
    inputBinding:
      prefix: -spws
      separate: true
      position: 53
  data-column:
    type: string?
    doc: "CORRECTED_DATA if it exists, otherwise DATA will be used."
    inputBinding:
      prefix: -data-column
      position: 54
  maxuvw-m:
    type: float?
    doc: "Set maximum baseline distance"
    inputBinding:
      prefix: -maxuvw-m
      position: 55
  minuvw-m:
    type: float?
    doc: "Set minimum baseline distance"
    inputBinding:
      prefix: -minuvw-m
      position: 56
  maxuv-l:
    type: float?
    doc: "Set maximum uv distance"
    inputBinding:
      prefix: -maxuv-l
      position: 57
  minuv-l:
    type: float?
    doc: "Set minimum uv distance"
    inputBinding:
      prefix: -minuv-l
      position: 58
  niter:
    type: int?
    doc: "Maximum number of clean iterations to perform"
    inputBinding:
      prefix: -niter
      position: 59
  threshold:
    type: float?
    doc: "Stopping clean thresholding in Jy"
    inputBinding:
      prefix: -threshold
      position: 60
  auto-threshold:
    type: float?
    doc: "Estimate noise level using a robust estimator and stop at sigma x stddev."
    inputBinding:
      prefix: -auto-threshold
      position: 61
  auto-mask:
    type: float?
    doc: "Construct a mask from found components and when a threshold of sigma is reached, continue cleaning with the mask down to the normal threshold."
    inputBinding:
      prefix: -auto-mask
      position: 62
  rms-background:
    type: boolean?
    doc: "Instead of using a single RMS for auto thresholding/masking, use a spatially varying RMS image"
    inputBinding:
      prefix: -rms-background
      position: 63
  rms-background-window:
    type: int?
    doc: "Size of window for creating the RMS background map, in number of PSFs."
    inputBinding:
      prefix: -rms-background-window
      position: 64
  rms-background-method:
    type: string?
    doc: "Either 'rms' (default, uses sliding window RMS) or 'rms-with-min' (use max(window rms,1.5/5window min))"
    inputBinding:
      prefix: -rms-background-method
      position: 65
  gain:
    type: float?
    doc: "Cleaning gain: Ratio of peak that will be subtracted in each iteration"
    inputBinding:
      prefix: -gain
      position: 66
  mgain:
    type: float?
    doc: "Cleaning gain for major iterations: Ratio of peak that will be subtracted in each major iteration. To use major iterations, 0.85 is a good value."
    inputBinding:
      prefix: -mgain
      position: 67
  join-polarizations:
    type: boolean?
    doc: "Perform cleaning by searching for peaks in the sum of squares of the polarizations, but subtract components from the individual images. Only possible when imaging two or four Stokes or linear parameters"
    inputBinding:
      prefix: -joinpolarizations
      position: 68
  joinchannels:
    type: boolean?
    doc: "Perform cleaning by searching for peaks in the MFS image, but subtract components from individual channels. This will turn on mfsweighting by default"
    inputBinding:
      prefix: -joinchannels
      position: 69
  multiscale:
    type: boolean?
    doc: "Clean on different scales. This is a new algorithm. This parameter invokes the v1.9 multiscale algorithm, which is slower but more accurate compared to the older algorithm, and therefore the recommended one to use. The older algorithm is now invoked with 'fast-multiscale'."
    inputBinding:
      prefix: -multiscale
      position: 70
  fast-multiscale:
    type: boolean?
    doc: "Clean on different scales. This is a new fast experimental algorithm. This method used to be invoked with 'multiscale' before v1.9, but the newer multiscale"
    inputBinding:
      prefix: -fast-multiscale
      position: 71
  multiscale-scale-bias:
    type: float?
    doc: "Parameter to prevent cleaning small scales in the large-scale iterations. A higher bias will give more focus to larger scales"
    inputBinding:
      prefix: -multiscale-scale-bias
      position: 72
  multiscale-scales:
    type: int[]?
    doc: "Sets a list of scales to use in multi-scale cleaning. If unset, WSClean will select the delta (zero) scale, scales starting at four times the synthesized PSF, and increase by a factor of two until the maximum scale is reached. Example: -multiscale-scales 0,5,12.5"
    inputBinding:
      prefix: -multiscale-scales
      separate: true
      position: 73
  iuwt:
    type: boolean?
    doc: "Use the IUWT deconvolution algorithm"
    inputBinding:
      prefix: -iuwt
      position: 74
  iuwt-snr-test:
    type: boolean?
    doc: "Stop IUWT when the SNR decreases. This might help limitting divergence, but can occasionally also stop the algorithm too early."
    inputBinding:
      prefix: -iuwt-snr-test
      position: 75
  cleanborder:
    type: float?
    doc: "Set the border size in which no cleaning is performed, in percentage of the width/height of the image. With an image size of 1000 and clean border of 1%, each border is 10 pixels."
    inputBinding:
      prefix: -cleanborder
      position: 76
  smallpsf:
    type: boolean?
    doc: "Resize the psf to speed up minor clean iterations"
    inputBinding:
      prefix: -smallpsf
      position: 79
  nonegative:
    type: boolean?
    doc: "Do not allow negative components during cleaning"
    inputBinding:
      prefix: -nonegative
      position: 80
  stopnegative:
    type: boolean?
    doc: "Stop on negative components"
    inputBinding:
      prefix: -stopnegative
      position: 81
  fit-spectral-pol:
    type: int?
    doc: "Fit a polynomial over frequency to each clean component. This has only effect when the channels are joined with 'joinchannels'"
    inputBinding:
      prefix: -fit-spectral-pol
      position: 82
  deconvolution-channels:
    type: int?
    doc: "Decrease the number of channels as specified by 'channelsout' to the given number for deconvolution. Only possible in combination with one of the 'fit-spectral' options. Proper residuals/restored images will only be returned when mgain < 1."
    inputBinding:
      prefix: -deconvolution-channels
      position: 83
  squared-channel-joining:
    type: boolean?
    doc: "Use with 'joinchannels' to perform peak finding in the sum of squared values over channels, instead of the normal sum. This is useful for imaging QU polarizations with non-zero rotation measures, for which the normal sum is insensitive."
    inputBinding:
      prefix: -squared-channel-joining
      position: 84
  force-dynamic-join:
    type: boolean?
    doc: "Use alternative joined clean algorithm (feature for testing)"
    inputBinding:
      prefix: -force-dynamic-join
      position: 85
  beamsize:
    type: float?
    doc: "Set a circular beam size (FWHM) in arcsec for restoring the clean components."
    inputBinding:
      prefix: -beamsize
      position: 86
  beamshape:
    type: int[]?
    doc: "Set the FWHM beam shape for restoring the clean components. Defaults units for maj and min are arcsec, and degrees for PA. Can be overriden, e.g. 'beamshape 1amin 1amin 3deg'. Default is use PSF FWHM sizes"
    inputBinding:
      prefix: -beamshape
      separate: true
      position: 87
  fitbeam:
    type: boolean?
    doc: "Determine beam shape by fitting the PSF."
    inputBinding:
      prefix: -fitbeam
      position: 88
  theoreticbeam:
    type: boolean?
    doc: "Write the beam in output fits files as calculated from the longest projected baseline. This method results in slightly less accurate beam size/integrated fluxes, but provides a beam size without making the PSF for quick imaging."
    inputBinding:
      prefix: -theoreticbeam
      position: 89
  nofitbeam:
    type: boolean?
    doc: "Do not determine beam shape from the PSF"
    inputBinding:
      prefix: -nofitbeam
      position: 90
  circularbeam:
    type: boolean?
    doc: "Force restoring beam to be circular"
    inputBinding:
      prefix: -circularbeam
      position: 91
  ellipticalbeam:
    type: boolean?
    doc: "Allow restoring beam to be elliptical"
    inputBinding:
      prefix: -ellipticalbeam
      position: 92
  fitsmask:
    type: File?
    doc: "Use the specified fits-file as mask during cleaning."
    inputBinding:
      prefix: -fitsmask
      position: 93
  casamask:
    type: Directory?
    doc: "Use the specified CASA mask as mask during cleaning."
    inputBinding:
      prefix: -casamask
      position: 94
  ms:
    type: Directory
    doc: "MS(s) to be imaged. If multiple mses are specified, they need to be phase-rotated to the same point on the sky"
    inputBinding:
      position: 95

outputs:
  images:
    type: File[]
    doc: "Output images"
    outputBinding:
      glob: $(inputs.name)*.fits
