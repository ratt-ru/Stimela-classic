cwlVersion: v1.1
class: CommandLineTool

requirements:
  DockerRequirement:
    dockerImageId: stimela/rfimasker:1.2.0
  InlineJavascriptRequirement: {}
  InitialWorkDirRequirement:
    listing:
    - entry: $(inputs.ms)
      writable: true

baseCommand: mask_ms.py

inputs:
  accumulation_mode:
    type:
      - "null"  # hack to make enum optional
      - type: enum
        symbols: [or,overide]
    doc: "Specifies whether mask should override current flags or be added (or) to the current"
    inputBinding:
      prefix: --accumulation_mode
  statistics:
    type: boolean?
    doc: "Computes and reports some statistics about the flagged RFI in the MS"
    inputBinding:
      prefix: --statistics
  memory:
    type: int?
    doc: "Maximum memory to consume in MB for the flag buffer"
    inputBinding:
      prefix: --memory
  spwid:
    type: int[]?
    doc: "SPW id (or ids if multiple MSs have been specified)"
    inputBinding:
      prefix: --spwid
      separate: true
  uvrange:
    type: string?
    doc: "UV range to select (CASA style range: lower~upper) for flagging. Leave blank for entire array"
    inputBinding:
      prefix: --uvrange
  simulate:
    type: boolean?
    doc: "Simulate only. Do not apply flags - useful for statistics"
    inputBinding:
      prefix: --simulate
  ms:
    type: Directory
    doc: "MS to flagged"
    inputBinding:
      valueFrom: $(self.path)
      position: 1000
  mask:
    type: File
    doc: "A numpy array of chan x (boolean, channel_centre[float64])"
    inputBinding:
      prefix: --mask

outputs:
  ms_out:
    type: Directory
    outputBinding:
      glob: $( inputs.ms.basename )
