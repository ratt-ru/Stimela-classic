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
      task = crasa.CasaTask("flagdata", **args)
      task.run()

baseCommand: python

inputs:
  vis:
    type: Directory
    doc: Name of MS file or calibration table
  mode:
    type:
      type: enum
      symbols: [manual, list, clip, quack, shadow, elevation, tfcrop, rflag, extend,
        unflag, summary]
    doc: Flagging mode
  field:
    type: string?
    doc: Field names or field index numbers:'' ==> all, field='0~2,3C286'
  spw:
    type: string?
    doc: "Spectral-window/frequency/channel: '' ==> all, spw='0:17~19'"
  antenna:
    type: string?
    doc: "Antenna/baselines: '' ==> all, antenna ='3,VA04'"
  timerange:
    type: string?
    doc: "Time range: '' ==> all,timerange='09:14:0~09:54:0'"
  correlation:
    type: string?
    doc: "Correlation: '' ==> all, correlation='XX,YY'"
  scan:
    type: string?
    doc: "Scan numbers: '' ==> all"
  intent:
    type: string?
    doc: "Observation intent: '' ==> all, intent='CAL*POINT*'"
  array:
    type: string?
    doc: "(Sub)array numbers: '' ==> all"
  uvrange:
    type: string?
    doc: "UV range: '' ==> all; uvrange ='0~100klambda', default units=meters"
  observation:
    type: string?
    doc: "Observation ID: '' ==> all"
  feed:
    type: string?
    doc: ' Multi-feed numbers: Not yet implemented'
  autocorr:
    type: boolean?
    doc: Flag only the auto-correlations
  inpfile:
    type: string[]?
    doc: Input ASCII file, list of files or Python list of strings with flag commands
  reason:
    type: string[]?
    doc: Select by REASON types
  tbuff:
    type: float[]?
    doc: List of time buffers (sec) to pad timerange in flag commands
  datacolumn:
    type: string?
    doc: Data column on which to operate (data,corrected,model,weight,etc.)
  clipminmax:
    type: float[]?
    doc: Range to use for clipping
  clipoutside:
    type: boolean?
    doc: Clip outside the range, or within it
  channelavg:
    type: boolean?
    doc: Average over channels (scalar average)
  clipzeros:
    type: boolean?
    doc: Clip zero-value data
  quackinterval:
    type: float?
    doc: Quack n seconds from scan beginning or end
  quackmode:
    type:
      type: enum
      symbols: [beg, endb, end, tail]
    doc: Quack mode. 'beg' ==> first n seconds of scan.'endb' ==> last n seconds of
      scan. 'end' ==> all but first n seconds of scan. 'tail' ==> all but last n seconds
      of scan.
  quackincrement:
    type: boolean?
    doc: Flag incrementally in time?
  tolerance:
    type: float?
    doc: Amount of shadow allowed (in meters)
  addantenna:
    type: File?
    doc: File name or dictionary with additional antenna names, positions and diameters
  lowerlimit:
    type: int?
    doc: Lower limiting elevation (in degrees)
  upperlimit:
    type: int?
    doc: Upper limiting elevation (in degrees)
  ntime:
    type: string?
    doc: Time-range to use for each chunk (in seconds or minutes)
  combinescans:
    type: boolean?
    doc: Accumulate data across scans depending on the value of ntime.
  timecutoff:
    type: float?
    doc: Flagging thresholds in units of deviation from the fit
  freqcutoff:
    type: float?
    doc: Flagging thresholds in units of deviation from the fit
  timefit:
    type:
      type: enum
      symbols: [poly, line]
    doc: Fitting function for the time direction (poly/line)
  freqfit:
    type:
      type: enum
      symbols: [poly, line]
    doc: Fitting function for the frequency direction (poly/line)
  maxnpieces:
    type: int?
    doc: Number of pieces in the polynomial-fits (for 'freqfit' or 'timefit' ='poly')
  flagdimension:
    type:
      type: enum
      symbols: [freq, time, freqtime, timefreq]
    doc: Dimensions along which to calculate fits (freq/time/freqtime/timefreq)
  usewindowstats:
    type:
      type: enum
      symbols: [none, sum, std, both]
    doc: Calculate additional flags using sliding window statistics (none,sum,std,both)
  halfwin:
    type: int?
    doc: Half-width of sliding window to use with 'usewindowstats' (1,2,3).
  extendflags:
    type: boolean?
    doc: Extend flags along time, frequency and correlation.
  extendpols:
    type: boolean?
    doc: If any correlation is flagged, flag all correlations
  growtime:
    type: float?
    doc: Flag all 'ntime' integrations if more than X% of the timerange is flagged
      (0-100)
  growfreq:
    type: float?
    doc: Flag all selected channels if more than X% of the frequency range is flagged(0-100)
  growaround:
    type: boolean?
    doc: Flag data based on surrounding flags
  flagneartime:
    type: boolean?
    doc: Flag one timestep before and after a flagged one (True/False)
  flagnearfreq:
    type: boolean?
    doc: Flag one channel before and after a flagged one (True/False)
  minrel:
    type: float?
    doc: minimum number of flags (relative)
  maxrel:
    type: float?
    doc: maximum number of flags (relative)
  minabs:
    type: int?
    doc: minimum number of flags (absolute)
  maxabs:
    type: int?
    doc: maximum number of flags (absolute). Use a negative value to indicate infinity.
  spwchan:
    type: boolean?
    doc: Print summary of channels per spw
  spwcorr:
    type: boolean?
    doc: Print summary of correlation per spw
  basecnt:
    type: boolean?
    doc: Print summary counts per baseline
  name:
    type: string?
    doc: Name of this summary report (key in summary dictionary)
  action:
    type:
      type: enum
      symbols: [none, apply, calculate]
    doc: Action to perform in MS and/or in inpfile (none/apply/calculate)
  display:
    type:
      type: enum
      symbols: [data, report, both]
    doc: Display data and/or end-of-MS reports at runtime (data/report/both).
  flagbackup:
    type: boolean?
    doc: Back up the state of flags before the run
  savepars:
    type: boolean?
    doc: Save the current parameters to the FLAG_CMD table or to a file
  cmdreason:
    type: string?
    doc: Reason to save to output file or to FLAG_CMD table.
  winsize:
    type: int?
    doc: Number of timesteps in the sliding time window [aips:fparm(1)]
  timedev:
    type: float?
    doc: 'Time-series noise estimate : [aips:noise]'
  freqdev:
    type: float?
    doc: 'Spectral noise estimate : [aips:scutoff]'
  timedevscale:
    type: float?
    doc: 'Threshold scaling for timedev : [aips:fparm(9)] '
  freqdevscale:
    type: float?
    doc: 'Threshold scaling for freqdev : [aips:fparm(10)]'
  spectralmax:
    type: float?
    doc: Flag whole spectrum if freqdev is greater than spectralmax
  spectralmin:
    type: float?
    doc: 'Flag whole spectrum if freqdev is less than spectralmin : [aips:fparm(5)]'
  chanbin:
    type: int?
    doc: Bin width for channel average in number of input channels
  outfile:
    type: string
    doc: Name of output file to save current parameters. If empty, save to FLAG_CMD

outputs:
  vis_out:
    type: Directory
    outputBinding:
      outputEval: $(inputs.vis)
  outfile_out:
    type: File
    outputBinding:
      glob: $(inputs.outfile)
