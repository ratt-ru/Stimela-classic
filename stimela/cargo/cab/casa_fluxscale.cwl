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
      - entry: $(inputs.fluxtable_out)
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
      print(args, file=sys.stderr)
      task = crasa.CasaTask("fluxscale", **args)
      task.run()

baseCommand: python

inputs:
  vis:
    type: Directory
    doc: Name of input visibility file (MS)
  caltable:
    type: Directory?
    doc: Name of input calibration table
  reference:
    type: string[]?
    doc: Reference field name(s) (transfer flux scale FROM)
  transfer:
    type: string[]?
    doc: Transfer field name(s) (transfer flux scale TO), '' -> all
  listfile:
    type: File?
    doc: Name of listfile that contains the fit information. Default is (no file).
  append:
    type: boolean?
    doc: Append solutions?
  refspwmap:
    type: string[]?
    doc: Scale across spectral window boundaries.  See help fluxscale
  incremental:
    type: boolean?
    doc: incremental caltable
  fitorder:
    type: int?
    doc: order of spectral fitting
  overwrite:
    type: boolean?
    doc: overwrite fluxtable
  fluxscale:
    type: string
    doc: Name of output, flux-scaled calibration table
    
outputs:
  fluxscale_out:
    type: Directory
    outputBinding:
      glob: $(inputs.fluxtable)
  vis_out:
    type: Directory
    outputBinding:
      outputEval: $(inputs.vis)
