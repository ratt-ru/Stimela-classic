import stimela


DIRS = {
    "indir": "input",
    "outdir": "outdir",
    "msdir": "msdir",
}

MS = "example.ms"


recipe = stimela.Recipe("test recipe", dirs=dirs, backend=docker)

recipe.add("simms", name="makems", params={
    "msname": MS,
    "synthesis": 1,
    "telescope": "kat-7",
    "dtime": 1,
    "dfreq": "1MHz",
    "nchan": 5,
}, 
info="Make simulated MS")

recipe.add("wscleam", name="image", params={
    "ms": recipe.makems.outputs.ms,
    "name": "example",
    "scale": 1,
    "size": 512,
    "make-psf-only": True,
    "weight": "uniform",
},
info="Image MS PSF")

recipe.run()
