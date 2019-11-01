import stimela

recipe = stimela.Recipe("simple_simulation", indir="input", outdir="output", cachedir="cachedir")

recipe.add("simms", "makems", {
    "msname"      : "test.ms",
    "telescope" : "kat-7",
    }, 
    doc="Create Empty MS")

recipe.add("simulator", "simsky", {
    "msname"        : recipe.makems.outputs["msname_out"],
    "skymodel"  : "nvss1deg.lsm.html",
    "config"    : "tdlconf.profiles",
},
    doc="Simulate sky model")

recipe.add("wsclean", "makeimage", {
    "msname" : recipe.simsky.outputs["msname_out"],
    "name"  : "test",
    "scale" : "30asec",
    "size"  : [512, 512]
},
    doc="Image data")

recipe.collect_outputs(["makeimage"])
recipe.run()
