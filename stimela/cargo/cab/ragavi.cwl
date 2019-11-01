cwlVersion: v1.1
class: CommandLineTool

requirements:
  DockerRequirement:
    dockerPull: stimela/ragavi:1.2.0
  InitialWorkDirRequirement:
    listing:
      - entry: $(inputs.table)
        writable: true

baseCommand: ragavi

inputs:
  ant:
    type: string?
    doc: Plot only this antenna, or comma-separated list of antennas. Default plots
      all
    inputBinding:
      prefix: --ant
  corr:
    type: int?
    doc: Correlation index to plot (usually just 0 or 1)
    inputBinding:
      prefix: --corr
  cmap:
    type: string?
    doc: Matplotlib colour map to use for antennas (default=coolwarm)
    inputBinding:
      prefix: --cmap
  doplot:
    type: 
      type: enum
      symbols: [ap, ri]
    default: ap
    doc: Plot complex values as amp and phase (ap) or real and imag (ri)
    inputBinding:
      prefix: --doplot
  field:
    type: int
    doc: Field ID to plot
    inputBinding:
      prefix: --field
  fieldint[]:
    type: int[]?
    doc: Field ID to plot
    inputBinding:
      prefix: --fieldint[]
  gaintype:
    type: 
      type: enum
      symbols: [B, F, G, K]
    doc: The gain type of table(s) to be plotted. Options
    inputBinding:
      prefix: --gaintype
  table:
    type: Directory
    doc: Gain table(s) to plot
    inputBinding:
      prefix: --table
  t0:
    type: float?
    doc: Minimum time to plot (default = full range)
    inputBinding:
      prefix: --t0
  t1:
    type: float?
    doc: Maximum time to plot (default = full range)
    inputBinding:
      prefix: --t1
  yu0:
    type: float?
    doc: Minimum y-value to plot for upper panel (default=full range)
    inputBinding:
      prefix: --yu0
  yu1:
    type: float?
    doc: Maximum y-value to plot for upper panel (default=full range)
    inputBinding:
      prefix: --yu1
  yl0:
    type: float?
    doc: Minimum y-value to plot for lower panel (default=full range)
    inputBinding:
      prefix: --yl0
  yl1:
    type: float?
    doc: Maximum y-value to plot for lower panel (default=full range)
    inputBinding:
      prefix: --yl1
  htmlname:
    type: string
    doc: Output html file name
    inputBinding:
      prefix: --htmlname 
  plotname:
    type: string?
    doc: Output png/svg image file name
    inputBinding:
      prefix: --plotname

outputs:
  htmlout:
    type: File
    outputBinding:
      glob: $(inputs.htmlname)*.html
  plotout:
    type: File?
    outputBinding:
      glob: $(inputs.plotname)*.png
