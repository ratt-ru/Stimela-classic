import stimela

recipe = stimela.Recipe("simple_simulation", indir="input", outdir="output", cachedir="cachedir")

recipe.add("simms", "makems", {
    "msname"      : "test.ms",
    "telescope" : "kat-7",
    }, 
    doc="Create Empty MS")

recipe.add("simulator", "simsky", {
    "ms"        : recipe.makems.outputs["ms"],
    "skymodel"  : "nvss1deg.lsm.html",
    "config"    : "tdlconf.profiles",
},
    doc="Simulate sky model")

recipe.add("wsclean", "makeimage", {
    "ms"    : recipe.simsky.outputs["ms_out"],
    "name"  : "test",
    "scale" : "30asec",
    "size"  : 512,
},
    doc="Image data")

recipe.collect_outputs(["makeimage"])
recipe.run()
