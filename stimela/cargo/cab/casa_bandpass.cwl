cwlVersion: v1.1
class: CommandLineTool

requirements:
  EnvVarRequirement:
    envDef:
      USER: root
  DockerRequirement:
    dockerPull: stimela/casa:1.2.0
  InlineJavascriptRequirement: {}
  InitialWorkDirRequirement:
    listing:
      - entry: $(inputs.vis)
        writable: true
      - entry: $(inputs.caltable_append)
        writable: true
  InplaceUpdateRequirement:
    inplaceUpdate: true

arguments:
  - prefix: -c
    valueFrom: |
      from __future__ import print_function
      import Crasa.Crasa as crasa
      import sys 

      # JavaScript uses lowercase for bools
      true = True
      false = False
      null = None

      args = ${
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
      gaintables = args.get("gaintable_list")
      if gaintables:
          for i, gaintable in enumerate(gaintables):
              if isinstance(gaintable, dict):
                  gaintables[i] = gaintable["path"]
          args["gaintable"] = gaintables
      caltable = args.get("caltable_append", None)
      if caltable:
          args["caltable"] = caltable
      task = crasa.CasaTask("bandpass", **args)
      task.run()

baseCommand: python

inputs:
  vis:
    type: Directory
    doc: Name of input visibility file
  field:
    type: string?
    doc: Field Name or id
  spw:
    type: string?
    doc: Spectral windows e.g. '0~3', '' is all
  selectdata:
    type: boolean?
    doc: Other data selection parameters
  timerange:
    type: string[]?
    doc: Range of time to select from data, e.g. timerange = 'YYYY/MM/DD/hh:mm:ss~YYYY/MM/DD/hh:mm:ss'
  uvrange:
    type: string[]?
    doc: Select data within uvrange
  antenna:
    type: string[]?
    doc: Select data based on antenna/baseline
  scan:
    type: string?
    doc: Scan number range
  observation:
    type: string[]?
    doc: Observation ID range
  msselect:
    type: string?
    doc: Optional complex data selection (ignore for now)
  solint:
    type: string
    doc: Solution interval in time[,freq]
  combine:
    type: string?
    doc: Data axes which to combine for solve (obs, scan, spw, and/or field)
  refant:
    type: string?
    doc: Reference antenna name(s)
  minblperant:
    type: int?
    doc: Minimum baselines _per antenna_ required for solve
  minsnr:
    type: float?
    doc: Reject solutions below this SNR (only applies for bandtype = B)
  solnorm:
    type: boolean?
    doc: Normalize average solution amplitudes to 1.0
  bandtype:
    type:
      type: enum
      symbols: [B, BPOLY]
    default: B
    doc: Type of bandpass solution (B or BPOLY)
  fillgaps:
    type: int?
    doc: Fill flagged solution channels by interpolation
  degamp:
    type: int?
    doc: Polynomial degree for BPOLY amplitude solution
  degphase:
    type: int?
    doc: Polynomial degree for BPOLY phase solution
  visnorm:
    type: boolean?
    doc: Normalize data prior to BPOLY solution
  maskcenter:
    type: int?
    doc: Number of channels to avoid in center of each band
  maskedge:
    type: int?
    doc: Fraction of channels to avoid at each band edge (in %)
  smodel:
    type: float[]?
    doc: Point source Stokes parameters for source model.
  append:
    type: boolean?
    doc: Append solutions to the (existing) table
  docallib:
    type: boolean?
    doc: Use callib or traditional cal apply parameters
  gaintable:
    type: Directory?
    doc: Gain calibration table(s) to apply on the fly
  gaintable_list:
    type: Directory[]?
    doc: Gain calibration table(s) to apply on the fly
  gainfield:
    type: string[]?
    doc: Select a subset of calibrators from gaintable(s)
  interp:
    type: string[]?
    doc: Interpolation mode (in time) to use for each gaintable
  spwmap:
    type: string[]?
    doc: Spectral windows combinations to form for gaintables(s)
  callib:
    type: File?
    doc: Cal Library filename
  parang:
    type: boolean?
    doc: Apply parallactic angle correction
  caltable:
    type: string?
    doc: Name of output gain calibration table
  caltable_append:
    type: Directory?
    doc: Name of output gain calibration table

outputs:
  caltable_out:
    type: Directory?
    outputBinding:
      glob: $(inputs.caltable)
  caltable_append_out:
    type: Directory?
    outputBinding:
      outputEval: $(inputs.caltable_append)
  vis_out:
    type: Directory
    outputBinding:
      outputEval: $(inputs.vis)
