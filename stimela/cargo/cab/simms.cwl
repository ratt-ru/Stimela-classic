cwlVersion: v1.1
class: CommandLineTool

baseCommand: simms

requirements:
  DockerRequirement:
    dockerImageId: stimela/simms:1.2.0
  InlineJavascriptRequirement: {}
  EnvVarRequirement:
    envDef:
      USER: root

inputs:
  msname:
    type: string?
    doc: Name out simulated MS file
    inputBinding:
      prefix: --name

  telescope:
    type: string
    inputBinding:
      prefix: --tel

  ra:
    type: string?
    doc: Phase tracking centre of observation

  dec:
    type: string?
    doc: Phase tracking centre of observation

  synthesis:
    type: float?
    doc: Synthesis time of observation
    inputBinding:
      prefix: --synthesis-time

  dtime:
    type: float?
    doc: Integration time
    inputBinding:
      prefix: --dtime

  freq0:
    type: float?
    doc: Start frequency of observation
    inputBinding:
      prefix: --freq0

  dfreq:
    type: float?
    doc: Channel width
    inputBinding:
      prefix: --dfreq

  nchan:
    type: int?
    doc: Number of channels
    inputBinding:
      prefix: --nchan

outputs:
  msname_out:
    type: Directory
    outputBinding:
      glob: $(inputs.msname)
