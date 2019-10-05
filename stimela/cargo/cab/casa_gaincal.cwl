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
      gaintables = args.pop("gaintable_list", None)
      if gaintables:
          for i, gaintable in enumerate(gaintables):
              if isinstance(gaintable, dict):
                  gaintables[i] = gaintable["path"]
          args["gaintable"] = gaintables
      caltable = args.get("caltable_append", None)
      print(args)
      if caltable:
          args["caltable"] = caltable
      task = crasa.CasaTask("gaincal", **args)
      task.run()

baseCommand: python

inputs:
  vis:
    type: Directory
    doc: Name of input visibility file
  field:
    type: string?
    doc: Select field using field id(s) or field name(s)
  spw:
    type: string?
    doc: Select spectral window/channels
  selectdata:
    type: boolean?
    doc: Other data selection parameters
  timerange:
    type: string?
    doc: Select data based on time range
  uvrange:
    type: string?
    doc: Select data within uvrange (default units meters)
  antenna:
    type: string?
    doc: Select data based on antenna/baseline
  scan:
    type: string?
    doc: Scan number range
  observation:
    type: string?
    doc: Select by observation ID(s)
  msselect:
    type: string?
    doc: Optional complex data selection (ignore for now)
  solint:
    type: string?
    doc: "Solution interval: egs. 'inf', '60s' (see help)"
  combine:
    type: string?
    doc: Data axes which to combine for solve (obs, scan, spw, and/or, field)
  preavg:
    type: float?
    doc: Pre-averaging interval (sec) (rarely needed)
  refant:
    type: string?
    doc: Reference antenna name(s)
  minblperant:
    type: int?
    doc: Minimum baselines _per antenna_ required for solve
  minsnr:
    type: float?
    doc: Reject solutions below this SNR
  solnorm:
    type: boolean?
    doc: Normalize average solution amplitudes to 1.0 (G, T only)
  gaintype:
    type:
      type: enum
      symbols: [G, T, GSPLINE, K, KCROSS]
    default: G
    doc: Type of gain solution (G,T,GSPLINE,K,KCROSS)
  splinetime:
    type: float?
    doc: Spline timescale(sec); All spw's are first averaged.
  npointaver:
    type: int?
    doc: The phase-unwrapping algorithm
  phasewrap:
    type: float?
    doc: Wrap the phase for jumps greater than this value (degrees)
  smodel:
    type: string[]?
    doc: Point source Stokes parameters for source model.
  calmode:
    type:
      type: enum
      symbols: [ap, p, a]
    default: ap
    doc: "Type of solution: ('ap', 'p', 'a')"
  append:
    type: boolean?
    doc: Append solutions to the (existing) table
  docallib:
    type: boolean?
    doc: Use callib or traditional cal apply parameters
  callib:
    type: File?
    doc: Cal Library filename
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
    doc: Temporal interpolation for each gaintable (=linear)
  spwmap:
    type: string[]?
    doc: Spectral windows combinations to form for gaintables(s)
  parang:
    type: boolean?
    doc: Apply parallactic angle correction on the fly
  caltable:
    type: string
    doc: Name of output gain calibration table
  caltable_append:
    type: Directory?
    doc: Path to existing table that gain solutions should be appended to, if appending to existing table.

outputs:
  caltable_out:
    type: Directory
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
