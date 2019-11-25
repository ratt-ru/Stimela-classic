cwlVersion: v1.1
class: CommandLineTool

requirements:
  DockerRequirement:
    dockerPull: stimela/tigger:1.2.0
  InlineJavascriptRequirement: {}
  InplaceUpdateRequirement:
    inplaceUpdate: true

baseCommand: tigger-convert

inputs:
  output_skymodel:
    inputBinding:
      position: 2
    doc: Output skymodel file name
    type: string
  app_to_int:
    inputBinding:
      prefix: --app-to-int
    doc: "Treat fluxes as apparent, and rescale them into intrinsic using the supplied\
      \ primary beam model (see 'primary-beam' option)."
    type: boolean?
  remove_source:
    inputBinding:
      prefix: --remove-source
    doc: ' Removes the named source(s) from the model. NAME may contain * and ? wildcards.'
    type: string?
  cluster_dist:
    inputBinding:
      prefix: --cluster-dist
    doc: Distance parameter for source clustering, 0 to disable. Default is 60.
    type: float?
  tags:
    inputBinding:
      prefix: --tags
    doc: Extract sources with the specified tags.
    type: string?
  type:
    inputBinding:
      prefix: --type
    doc: Input model type
    type:
      symbols: [Tigger, ASCII, BBS, NEWSTAR, AIPSCC, AIPSCCFITS, Gaul, auto]
      type: enum
  int_to_app:
    inputBinding:
      prefix: --int-to-app
    doc: "Treat fluxes as intrinsic, and rescale them into apparent using the supplied\
      \ primary beam model (see 'primary-beam' option)."
    type: boolean?
  primary_beam:
    inputBinding:
      prefix: --primary-beam
    doc: "Apply a primary beam expression to estimate apparent fluxes. Any valid Python\
      \ expression using the variables 'r' and 'fq' is accepted. Use 'refresh' to\
      \ re-estimate fluxes using the current expression. Example (for the WSRT-like\
      \ 25m dish PB): 'cos(min(65*fq*1e-9*r,1.0881))**6'. OR: give a set of FITS primary\
      \ beam patterns of the form e.g. FILENAME_$(xy)_$(reim).fits, these are the\
      \  same FITS files used in MeqTrees pybeams_fits."
    type: File?
  pa_range:
    inputBinding:
      prefix: --pa-range
    doc: Rotate the primary beam pattern through a range of parallactic angles (in
      degrees) and use the average value over PA.
    type: float[]?
  prefix:
    inputBinding:
      prefix: --prefix
    doc: Prefix all source names with the given string
    type: string?
  help_format:
    inputBinding:
      prefix: --help-format
    doc: Prints help on format strings.
    type: boolean?
  enable_plots:
    inputBinding:
      prefix: --enable-plots
    doc: Enables various diagnostic plots
    type: boolean?
  beam_freq:
    inputBinding:
      prefix: --beam-freq
    doc: "Use given frequency (in MHz) for primary beam model, rather than the model\
      \ reference frequency"
    type: float?
  linear_pol:
    inputBinding:
      prefix: --linear-pol
    doc: Use XY basis correlations for beam filenames and Mueller matrices.
    type: boolean?
  output_format:
    inputBinding:
      prefix: --output-format
    doc: "Output format, for ASCII or BBS tables. If the model was originally imported\
      \ from an ASCII or BBS table, the default output format will be the same as the\
      \ original format."
    type:
      symbols: [Tigger, ASCII, BBS, NEWSTAR, AIPSCC, AIPSCCFITS, Gaul, auto]
      type: enum
  refresh_r:
    inputBinding:
      prefix: --refresh-r
    doc: "Recompute the 'r' (radial distance from center) attribute of each source\
      \ based on the current field  center. 'ref-freq'=MHz Set or change the reference\
      \ frequency of the model."
    type: boolean?
  center:
    inputBinding:
      prefix: --center
    doc: "Override coordinates of the nominal field center specified in the input model.\
      \ Use the form 'Xdeg,Ydeg' or 'Xdeg,Yrad' to specify RA,Dec in degrees or radians,\
      \ or else a a pyrap.measures direction string of the form REF,C1,C2, for example\
      \ 'j2000,1h5m0.2s,+30d14m15s'. See the pyrap.measures documentation for more details."
    type: string?
  radial_step:
    inputBinding:
      prefix: --radial-step
    doc: Size of one step in radial distance for the COPART scheme.
    type: float?
  format:
    inputBinding:
      prefix: --format
    doc: "Input format, for ASCII or BBS tables. For ASCII tables, default is 'name\
      \ ra_h ra_m ra_s dec_d dec_m dec_s i q u v spi rm emaj_s emin_s pa_d freq0 tags...'.\
      \ For BBS tables, the default format is specified in the file header."
    type: string?
  field_id:
    inputBinding:
      prefix: --field-id
    doc: Field ID for 'pa-from-ms' calculation
    type: int[]?
  rename:
    inputBinding:
      prefix: --rename
    doc: "Rename sources according to the COPART (cluster ordering, P.A., radial distance,\
      \ type) scheme"
    type: boolean?
  beam_average_jones:
    inputBinding:
      prefix: --beam-average-jones
    doc: "Correct approach to rotational averaging is to convert Jones(PA) to Mueller(PA),\
      \ then average over PA. Tigger versions<=1.3.3 took the incorrect approach of\
      \ averaging Jones over PA, then converting to Mueller. Use this option to mimic\
      \ the old approach."
    type: boolean?
  verbose:
    inputBinding:
      prefix: --verbose
    doc: Increase verbosity
    type: boolean?
  fits_m_axis:
    inputBinding:
      prefix: --fits-m-axis
    doc: "CTYPE for M axis in the FITS PB file. Note that our internal M points North\
      \ (increasing Dec), if the FITS beam axis points the opposite way, prefix the\
      \ CTYPE with a '-' character."
    type: string?
  fits_l_axis:
    inputBinding:
      prefix: --fits-l-axis
    doc: CTYPE for L axis in the FITS PB file. Note that our internal L points East\
      \ (increasing RA), if the FITS beam axis points the opposite way, prefix the CTYPE\
      \ with a '-' character."
    type: string?
  beam_spi:
    inputBinding:
      prefix: --beam-spi
    doc: "Perform a spectral index fit to each source based on a frequency dependent\
      \ FITS beam, requires --primary-beam option to be used with a FITS file. Apply\
      \ this spectral index to LSM sources. Must supply a band width (centred on --beam-freq)\
      \ over which the beam spi is estimated"
    type: float?
  input_skymodel:
    inputBinding:
      position: 1
    doc: Input skymodel
    type: File
  newstar_app_to_int:
    inputBinding:
      prefix: --newstar-app-to-int
    doc: "Convert NEWSTAR apparent fluxes in input model to intrinsic. Only works for\
      \ NEWSTAR or NEWSTAR-derived input models."
    type: boolean?
  append_format:
    inputBinding:
      prefix: --append-format
    doc: Format of appended file, for ASCII or BBS tables. Default is to use 'format'.
    type:
      - "null"
      - type: enum
        symbols: [Tigger, ASCII, BBS, NEWSTAR, AIPSCC, AIPSCCFITS, Gaul, auto]
  min_extent:
    inputBinding:
      prefix: --min-extent
    doc: "Minimal source extent, when importing NEWSTAR or ASCII files. Sources with\
      \ a smaller extent will be treated as point sources."
    type: float?
  select:
    inputBinding:
      prefix: --select
    doc: "Selects a subset of sources by comparing the named TAG to a float VALUE.\
      \ '<>' represents the comparison operator, and can be one of == (or =),!=,<=,<,>,>=.\
      \ Alternatively, you may use the FORTRAN-style operators .eq.,.ne.,.le.,.lt.,.gt.,.ge.\
      \ Multiple select options may be given, in which case the effect is a logical-\
      \ AND. Note that VALUE may be followed by one of the characters d, m or s, in\
      \ which case it will be converted from degrees, minutes or seconds into radians.\
      \ This is useful for selections such as 'r<5d'. 'remove-nans' Removes the named\
      \ source(s) from the model. NAME may contain * and ? wildcards."
    type: string?
  pa:
    inputBinding:
      prefix: --pa
    doc: Rotate the primary beam pattern through a parallactic angle (in degrees).
    type: float?
  beam_clip:
    inputBinding:
      prefix: --beam-clip
    doc: "when using a FITS beam, clip (power) beam gains at this level to keep intrinsic\
      \ source fluxes from blowing up. Sources below this beamgain will be tagged\
      \ 'nobeam'. Default: 0.001"
    type: float?
  pa_from_ms:
    inputBinding:
      prefix: --pa-from-ms
    doc: "Rotate the primary beam pattern through a range of parallactic angles as\
      \ given by the MS and take the average over time. This is more accurate than --pa-range."
    type: File[]?
  append:
    inputBinding:
      prefix: --append
    doc: Append this model to input-skymodel, then write to output-skymodel
    type: File?
  force:
    inputBinding:
      prefix: --force
    doc: Forces overwrite of output model.
    type: boolean?
  beam_diag:
    inputBinding:
      prefix: --beam-diag
    doc: "Use diagonal Jones terms only for beam model. Default is to use all four\
      \ terms if available."
    type: boolean?
  force_beam_spi_wo_spectrum:
    inputBinding:
      prefix: --force-beam-spi-wo-spectrum
    doc: Apply beam-derived spectral indices even to sources without an intrinsic\
      \ spectrum. Default is to only apply to sources that already have a spectrum.\
      \ 'beam-nopol' apply intensity beam model only, ignoring polarization. Default\
      \ is to use polarization. 'beam-diag' use diagonal Jones terms only for beam model.\
      \ Default is to use all four terms if available."
    type: boolean?
  newstar_int_to_app:
    inputBinding:
      prefix: --newstar-int-to-app
    doc: "Convert NEWSTAR intrinsic fluxes in input model to apparent. Only works for\
      \ NEWSTAR or NEWSTAR-derived input models."
    type: boolean?
  output_type:
    inputBinding:
      prefix: --output-type
    doc: Output model type.
    type:
      symbols: [Tigger, ASCII, BBS, NEWSTAR, auto]
      type: enum
  append_type:
    inputBinding:
      prefix: --append-type
    doc: "Append another model to input model. May be given multiple times.
      \ --append-type=TYPE  Appended model type (Tigger, ASCII, BBS, NEWSTAR, AIPSCC, AIPSCCFITS, Gaul, auto).
      \ Default is none."
    type:
      - "null"
      - type: enum
        symbols: [Tigger, ASCII, BBS, NEWSTAR, AIPSCC, AIPSCCFITS, Gaul, auto]
  recenter:
    inputBinding:
      prefix: --recenter
    doc: "Shift the sky model from the nominal center to a different field center.
      \ COORDINATES specified as per the --center option."
    type: string?
  merge_clusters:
    inputBinding:
      prefix: --merge-clusters
    doc: "Merge source clusters bearing the specified tags, replacing them with a single
      \ point source. Multiple tags may be given separated by commas. Use 'ALL' to merge
      \ all clusters."
    type: string?

outputs:
  out_model:
    type: File
    outputBinding:
      glob: $(inputs.output_skymodel)
