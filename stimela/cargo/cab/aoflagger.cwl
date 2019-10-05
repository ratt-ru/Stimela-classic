cwlVersion: v1.1
class: CommandLineTool

requirements:
  DockerRequirement:
    dockerPull: stimela/aoflagger:1.2.0
  InlineJavascriptRequirement:
  InitialWorkDirRequirement:
    listing:
    - entry: $(inputs.ms)
      writable: true

baseCommand: aoflagger

inputs:
  verbose:
    type: boolean?
    doc: "Produce verbose output"
    inputBinding:
      prefix: -v
  j:
    type: int?
    doc: "overrides the number of threads specified in the strategy (default: one thread for each CPU core)"
    inputBinding:
      prefix: -j
  indirect-read:
    type: boolean?
    doc: "will reorder the measurement set before starting, which is normally faster but requires free disk space to reorder the data to"
    inputBinding:
      prefix: -indirect-read
  memory-read:
    type: boolean?
    doc: "will read the entire measurement set in memory. This is the fastest, but requires much memory."
    inputBinding:
      prefix: -memory-read
  auto-read-mode:
    type: boolean?
    doc: "will select either memory or direct mode based on available memory"
    inputBinding:
      prefix: -auto-read-mode
  uvw:
    type: boolean?
    doc: "reads uvw values (some exotic strategies require these)"
    inputBinding:
      prefix: -uvw
  column:
    type: string?
    doc: "specify column to flag"
    inputBinding:
      prefix: -column
  skip-flagged:
    type: boolean?
    doc: "will skip an ms if it has already been processed by AOFlagger according to its HISTORY table."
    inputBinding:
      prefix: -skip-flagged
  bands:
    type: int?
    doc: "comma separated list of (zero-indexed) band ids to process"
    inputBinding:
      prefix: -bands
      separate: true
  fields:
    type: string?
    doc: "Field ID(s). Comma separated string if more than one field"
    inputBinding:
      prefix: -fields
  ms:
    type: Directory
    doc: "MS name(s) to be flagged"
    inputBinding:
      position: 100
      valueFrom: $(self.path)
  strategy:
    type: File?
    doc: "specifies a possible customized strategy"
    inputBinding:
      prefix: -strategy

outputs:
  ms_out:
    type: Directory
    outputBinding:
       outputEval: $(inputs.ms)
