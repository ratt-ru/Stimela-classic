import stimela

PREFIX = "selfcal"

recipe = stimela.Recipe("selfcal_simulation",
                        indir="input",
                        outdir="output",
                        cachedir="cachedir")

recipe.add("simms", "makems", {
    "msname"               :   "meerkat_SourceRecovery.ms",
    "telescope"            :   "meerkat",
    "direction"            :   "J2000,0deg,-30deg",
    "synthesis"            :   0.5,      # in hours
    "dtime"                :   5,        # in seconds
    "freq0"                :   1.42e9,   # in hertz
    "dfreq"                :   1e6,      # in hertz
    "nchan"                :   4,
    },
    doc="Create Empty MS")

recipe.add("simulator", "simsky", {
    "msname"               :   recipe.makems.outputs["msname_out"],
    "config"               :   "tdlconf.profiles",
    "use_smearing"         :   False,
    "sefd"                 :   551,  # in Jy
    "output_column"        :   "DATA",
    "skymodel"             :   "point_skymodel.txt"
},
    doc="Simulate sky model")

recipe.add("wsclean", "makeimage", {
    "msname"               :   recipe.simsky.outputs["msname_out"],
    "name"                 :   PREFIX,
    "datacolumn"           :   "DATA",
    "scale"                :   "1asec",
    "channels_out"         :   2,
    "join_channels"        :   True,
    "mgain"                :   0.95,
    "scale"                :   "1.0asec",
    "niter"                :   10000,
    "auto_threshold"       :   5,
    "size"                 :   [256, 256]
},
    doc="Image data")

recipe.add("pybdsf", "sourcefinder", {
    "filename"     :   recipe.makeimage.outputs["image_out"],
    "outfile"      :   "{}-catalog.fits".format(PREFIX),
    "format"       :   "fits",
    "thresh_isl"   :   20,
    "thresh_pix"   :   10,
},
    doc="Source finding")


recipe.add("bdsf_fits2lsm", "convertfits", {
    "infile"             :   recipe.sourcefinder.outputs["model_out"],
    "phase_centre_image" :   recipe.makeimage.outputs["image_out"],
#    "phase_centre_coord" :   [0.0, -30.0],
    "outfile"            :   "{}-catalog.lsm.html".format(PREFIX)
},
    doc="Convert model catalog")

recipe.add("tigger_convert", "convertcatalog", {
    "input_skymodel"     :   recipe.convertfits.outputs["model_out"],
    "output_skymodel"    :   "{}-catalog_conv.lsm.html".format(PREFIX),
    "output_format"      :   "Tigger",
    "output_type"        :   "Tigger",
    "type"               :   "auto",
    "rename"             :   True,
},
    doc="Convert model catalog")

recipe.add('cubical', "calibration", {
    "data_ms"              :   recipe.makeimage.outputs["msname_out"],
    "data_column"          :   "DATA",
    "model_lsm"            :   recipe.convertcatalog.outputs["models_out"],
#    "model_column"         :   ['MODEL_DATA'],
    "model_expression"     :   ["lsm_0"],
    "data_time_chunk"      :   24, #128,
    "data_freq_chunk"      :   12, #1024,
    "sel_ddid"             :   "0",
    "dist_ncpu"            :   16,
    "sol_jones"            :   "G",
    "sol_term_iters"       :   "50",
    "out_name"             :   PREFIX,
    "out_mode"             :   "sc",
    "weight_column"        :   "WEIGHT",
    "montblanc_dtype"      :   "float",
    "g_type"               :   "complex-2x2",
    "g_time_int"           :   16,
    "g_freq_int"           :   0,
    "g_save_to"            :   "{}_g-gains.parmdb".format(PREFIX),
    "bbc_save_to"          :   "{}_bbc-gains.parmdb".format(PREFIX),
    "g_clip_low"           :   0.5,
    "g_clip_high"          :   2.0,
    "madmax_enable"        :   True,
    "madmax_plot"          :   True,
    "madmax_threshold"     :   [0.0, 10.0],
    "madmax_estimate"      :   "corr",
    "out_plots"            :   True,
    "out_casa_gaintables"  :   True,
    "g_solvable"           :   True,
    "out_overwrite"        :   True,
    "log_boring"           :   True,
    "shared_memory"        :   4096,
    "montblanc_mem_budget" :   1024,
},
    doc="Calibration")

recipe.collect_outputs(["makems", "simsky", "makeimage", "sourcefinder", "calibration"])

recipe.run()
#recipe.init() # To only generate the cwl files (<name>.cwl  <name>.yml)
