## Auto generated cwl file
cwlVersion: v1.1
class: CommandLineTool

requirements:
 DockerRequirement:
    dockerImageId: stimela/tigger:1.2.0
  InitialWorkDirRequirement:
    listing:
    - entry: $(inputs.input-image)
      writable: true
    listing:
    - entry: $(inputs.input-skymodel)
      writable: true
    listing:
    - entry: $(inputs.psf-file)
      writable: true
    InplaceUpdateRequirement:
    inplaceUpdate: true

baseCommand: tigger-restore

inputs:
  f:
    type: boolean
    doc: "Forces overwrite of output model."
    inputBinding:
      prefix: --f
      position: 3
  type:
    type:
      type: enum
      symbols: [Tigger,ASCII,BBS,NEWSTAR,AIPSCC,AIPSCCFITS,Gaul,auto]
    doc: "Input model type"
    inputBinding:
      prefix: --type
      position: 4
  format:
    type: string
    doc: "Input format, for ASCII or BBS tables. For ASCII tables, default is 'name ra_h ra_m ra_s dec_d dec_m dec_s i q u v spi rm emaj_s emin_s pa_d freq0 tags...'. For BBS tables, the default format is specified in the file header."
    inputBinding:
      prefix: --format
      position: 5
  tags:
    type: string
    doc: "Extract sources with the specified tags."
    inputBinding:
      prefix: --tags
      position: 6
  num-sources:
    type: int
    doc: "Only restore the NSRC brightest sources"
    inputBinding:
      prefix: --num-sources
      position: 7
  scale:
    type: float[]
    doc: "Rescale model fluxes by given factor. If N is given, rescale N brightest only."
    inputBinding:
      prefix: --scale
      separate: true
      position: 8
  restoring-beam:
    type: float[]
    doc: "Specify restoring beam size, overriding BMAJ/BMIN/BPA keywords in input image. Use a single value (arcsec) for circular beam, or else supply major/minor size and position angle (deg)."
    inputBinding:
      prefix: --restoring-beam
      separate: true
      position: 9
  beamgain:
    type: float
    doc: "Apply beamgain atribute during restoration, if it's defined, and source is not tagged 'nobeam' 'ignore-nobeam' apply PB or beamgain even if source is tagged 'nobeam'"
    inputBinding:
      prefix: --beamgain
      position: 11
  freq:
    type: float
    doc: "Use this frequency (in MHz) (for spectral indices and primary beams)"
    inputBinding:
      prefix: --freq
      position: 12
  verbose:
    type: boolean
    doc: "Set verbosity level (0 is silent, higher numbers mean more messages)"
    inputBinding:
      prefix: --verbose
      position: 13
  timestamps:
    type: boolean
    doc: "Enable timestamps in debug messages (useful for timing)"
    inputBinding:
      prefix: --timestamps
      position: 14
  input-image:
    type: File
    doc: "Input image"
    inputBinding:
      prefix: --input-image
      position: 15
      valueFrom: $(self.basename)
  input-skymodel:
    type: File
    doc: "Sky model to restore to 'input-image'"
    inputBinding:
      prefix: --input-skymodel
      position: 16
      valueFrom: $(self.basename)
  psf-file:
    type: File
    doc: "Determine restoring beam size by fitting PSF file, overriding BMAJ/BMIN/BPA keywords in input image. 'clear' clear contents of FITS file before adding in sources apply model primary beam function during restoration, if it's defined, and source is not tagged 'nobeam'"
    inputBinding:
      prefix: --psf-file
      position: 17
      valueFrom: $(self.basename)

outputs:
  output-image:
    type: File
    doc: "Input image"
    outputBinding:
      glob: output-image
