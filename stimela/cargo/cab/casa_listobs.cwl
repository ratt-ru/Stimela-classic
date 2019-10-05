cwlVersion: v1.1
class: CommandLineTool

requirements:
  InlineJavascriptRequirement: {}
  EnvVarRequirement:
    envDef:
      USER: root
  DockerRequirement:
    dockerPull: stimela/casa:1.2.0
  InitialWorkDirRequirement:
    listing:
      - entry: $(inputs.vis)
        writable: true
  InplaceUpdateRequirement:
    inplaceUpdate: true

baseCommand: python

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
      task = crasa.CasaTask("listobs", **args)
      task.run()

inputs:
  vis:
    type: Directory
    doc: Name of input visibility file
  overwrite:
    type: boolean?
    doc: If True, tacitly overwrite listfile if it exists.
  selectdata:
    type: boolean?
    doc: Data selection parameters
  field:
    type: string?
    doc: Field names or field index numbers. ''==>all, field='0~2,3C286'
  spw:
    type: string?
    doc: spectral-window/frequency/channel
  antenna:
    type: string?
    doc: "Antenna/baselines: ''==>all, antenna='3,VA04'"
  timerange:
    type: string?
    doc: "time range: ''==>all,timerange='09:14:0~09:54:0'"
  correlation:
    type: string?
    doc: Select data based on correlation
  scan:
    type: string?
    doc: "scan numbers: ''==>all"
  intent:
    type: string?
    doc: "Select data based on observation intent: ''==>all"
  feed:
    type: string?
    doc: 'Multi-feed numbers: Not yet implemented'
  array:
    type: string?
    doc: "(sub)array numbers: ''==>all"
  uvrange:
    type: string?
    doc: "uv range: ''==>all; uvrange ='0~100klambda', default units=meters"
  observation:
    type: string?
    doc: "Select data based on observation ID: ''==>all"
  verbose:
    type: boolean?
    doc: Verbose output
  listunfl:
    type: boolean?
    doc: List unflagged row counts? If true, it can have significant negative performance
      impact.
  cachesize:
    type: int?
    doc: EXPERIMENTAL. Maximum size in megabytes of cache in which data structures
      can be held.
  listfile:
    type: string?
    doc: "Name of disk file to write output: ''==>to terminal"

outputs:
  listfile_out:
    type: File?
    outputBinding:
      glob: $(inputs.listfile)
  vis_out:
    type: Directory
    outputBinding:
      outputEval: $(inputs.vis)
