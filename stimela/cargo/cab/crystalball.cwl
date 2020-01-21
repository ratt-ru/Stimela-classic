cwlVersion: v1.1
class: CommandLineTool

requirements:
  DockerRequirement:
    dockerPull: stimela/codex-africanus:1.2.3
  InlineJavascriptRequirement: {}
  InitialWorkDirRequirement:
    listing:
      - entry: $(inputs.ms)
        writable: true
      - entry: $(inputs.sky_model)
  InplaceUpdateRequirement:
    inplaceUpdate: true

baseCommand: crystalball

inputs:
  points_only:
    type: boolean?
    inputBinding:
      prefix: --points-only
    doc: Select only point-type sources.
  exp_sign_convention:
    type:
      symbols: [casa, thompson]
      type: enum
    inputBinding:
      prefix: --exp-sign-convention
    doc: Sign convention to use for the complex exponential. 'casa' specifies the
      e^(2.pi.I) convention while 'thompson' specifies the e^(-2.pi.I) convention
      in the white book and Fourier analysis literature. Defaults to 'casa'
    default: casa
  row_chunks:
    type: int?
    inputBinding:
      prefix: --row-chunks
    doc: Number of rows of input .MS that are processed in a single chunk. If zero,
      it will be automatically determined.
  model_chunks:
    type: int?
    inputBinding:
      prefix: --model-chunks
    doc: Number of sky model components that are processed in a single chunk. If 0
      it will be set automatically
  num_workers:
    type: int?
    inputBinding:
      prefix: --num-workers
    doc: Explicitly set the number of worker threads
  within:
    type: File?
    inputBinding:
      prefix: --within
    doc: Optional. Give JS9 region file. Only sources within those regions will be
      included.
  memory_fraction:
    type: float?
    inputBinding:
      prefix: --memory-fraction
    doc: Fraction of system RAM that can be used. Used when setting automatically
      the chunk size.
  fields:
    type: string[]?
    inputBinding:
      prefix: --fields
    doc: Comma-separated list of Field names or ids which should be predicted. All
      fields are predicted by default.
  output_column:
    type: string?
    inputBinding:
      prefix: --output-column
    doc: Output visibility column
  ms:
    type: Directory
    inputBinding:
      position: 1
    doc: Input MS file
  spectra:
    type: boolean?
    inputBinding:
      prefix: --spectra
    doc: Optional. Model sources as non-flat spectra. The spectral coefficients and
      reference frequency must be present in the sky model.
  num_sources:
    type: int?
    inputBinding:
      prefix: --num-sources
    doc: Select only N brightest sources.
  sky_model:
    type: File?
    inputBinding:
      prefix: --sky-model
    doc: Name of file containing the sky model. Default is 'sky-model.txt'

outputs:
  msname_out:
    type: Directory
    doc: Output images
    outputBinding:
      outputEval: $(inputs.ms)
