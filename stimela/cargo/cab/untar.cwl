cwlVersion: v1.1
class: CommandLineTool

baseCommand: tar

arguments: 
  - xvf

inputs:
  mstar:
    type: File
    inputBinding:
      valueFrom: $(self.path)

outputs:
  ms:
    type: Directory
    outputBinding:
      glob: "*.ms"
