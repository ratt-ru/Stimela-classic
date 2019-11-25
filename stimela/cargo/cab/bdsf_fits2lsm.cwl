cwlVersion: v1.1
class: CommandLineTool

requirements:
  EnvVarRequirement:
    envDef:
      USER: root
  DockerRequirement:
    dockerPull: stimela/pybdsf:1.2.0
  InlineJavascriptRequirement: {}
  InitialWorkDirRequirement:
    listing:
      - entry: $(inputs.infile)
        writable: true
  InplaceUpdateRequirement:
    inplaceUpdate: true

baseCommand: python

arguments:
  - prefix: -c
    valueFrom: |

      import numpy
      import Tigger
      import tempfile
      from astLib.astWCS import WCS
      import astropy.io.fits as pyfits
      from Tigger.Models import SkyModel, ModelClasses

      # JavaScript uses lowercase for bools
      true = True
      false = False
      null = None

      kwargs = ${
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

      name = kwargs['outfile']
      model_image = kwargs['infile']['path']
      if 'phase_centre_image' in kwargs.keys():
          pc_image = kwargs['phase_centre_image']['path']
      else:
          pc_image = None
      if 'phase_centre_coord' in kwargs.keys():
          pc_coord = kwargs['phase_centre_coord']
      else:
          pc_coord = None

      # convert to Gaul file to Tigger LSM
      # First make dummy tigger model
      tfile = tempfile.NamedTemporaryFile(suffix='.txt')
      tfile.flush()

      tname_lsm = name
      with open(tfile.name, "w") as stdw:
          stdw.write("#format:name ra_d dec_d i emaj_s emin_s pa_d\n")

      model = Tigger.load(tfile.name)
      tfile.close()

      def tigger_src(src, idx):

          name = "SRC%d" % idx

          flux = ModelClasses.Polarization(
              src["Total_flux"], 0, 0, 0, I_err=src["E_Total_flux"])
          ra, ra_err = map(numpy.deg2rad, (src["RA"], src["E_RA"]))
          dec, dec_err = map(numpy.deg2rad, (src["DEC"], src["E_DEC"]))
          pos = ModelClasses.Position(ra, dec, ra_err=ra_err, dec_err=dec_err)
          ex, ex_err = map(numpy.deg2rad, (src["DC_Maj"], src["E_DC_Maj"]))
          ey, ey_err = map(numpy.deg2rad, (src["DC_Min"], src["E_DC_Min"]))
          pa, pa_err = map(numpy.deg2rad, (src["PA"], src["E_PA"]))

          if ex and ey:
              shape = ModelClasses.Gaussian(
                  ex, ey, pa, ex_err=ex_err, ey_err=ey_err, pa_err=pa_err)
          else:
              shape = None
          source = SkyModel.Source(name, pos, flux, shape=shape)
          # Adding source peak flux (error) as extra flux attributes for sources,
          # and to avoid null values for point sources I_peak = src["Total_flux"]
          if shape:
              source.setAttribute("I_peak", src["Peak_flux"])
              source.setAttribute("I_peak_err", src["E_peak_flux"])
          else:
              source.setAttribute("I_peak", src["Total_flux"])
              source.setAttribute("I_peak_err", src["E_Total_flux"])
          return source

      RAs = []
      DECs = []
      with pyfits.open(model_image) as hdu:
          data = hdu[1].data

          for i, src in enumerate(data):
              model.sources.append(tigger_src(src, i))
              RAs.append(src['RA'])
              DECs.append(src['DEC'])

      if pc_image:
          wcs = WCS(pc_image)
          centre = wcs.getCentreWCSCoords()
          model.ra0, model.dec0 = map(numpy.deg2rad, centre)
      elif pc_coord:
          centre = pc_coord
          model.ra0, model.dec0 = map(numpy.deg2rad, centre)
      else:
          ras = numpy.array(RAs)
          decs = numpy.array(DECs)
          mean_ras = ras.mean()
          mean_dec = decs.mean()
          centre = (mean_ras, mean_dec)
          model.ra0, model.dec0 = map(numpy.deg2rad, centre)
      model.save(tname_lsm)

inputs:
  infile:
    type: File
    doc: Input catalog file
  phase_centre_image:
    type: File?
    doc: Fits image to get phase centre coordinates of skymodel
  phase_centre_coord:
    type: float[]?
    doc: Phase centre cordinates of skymodel (e.g. [0.0, -30.0]) in deg.
  outfile:
    type: string
    doc: Name of the output catalog file.

outputs:
  name_out:
    type: File
    outputBinding:
      glob: $(inputs.outfile)
