from otrera import Pipeline
import penthesilea

INPUT = "input"
OUTPUT = "output"
DATA = penthesilea.PENTHESILEA_DATA
MSDIR = "msdir"


## There is a configuration template for all Penthesilea executor image
CONFIGS = penthesilea.PENTHESILEA_CONFIG_TEMPLATES

# These are the names
simms_template = "simms_params.json"
simulator_template = "simulator_params.json"
imager_template = "imager_params.json"

MS = "meerkat_simulation_example.ms"
LSM = "nvss1deg.lsm.html"


# start oterera instance
pipeline = Pipeline("Simulation Example", CONFIGS, data=DATA, ms_dir=MSDIR)

# Make empty MS 
simms_dict = pipeline.readJson(simms_template)
simms_dict["msname"] = MS
simms_dict["telescope"] = "meerkat"
pipeline.add("ares/simms", "simms_example", simms_dict, input=INPUT, output=OUTPUT, 
             label="Creating MS")

# Simulate visibilities into it
simulator_dict = pipeline.readJson(simulator_template)
simulator_dict["msname"] = MS
simulator_dict["skymodel"] = LSM
pipeline.add("ares/simulator", "simulator_example", simulator_dict, input=INPUT, output=OUTPUT,
             label="Simulating visibilities")

## Image
# This is an example of how to iterate over a variable
# I want to make images with different uv-weights 

imager_dict = pipeline.readJson(imager_template)
imager_dict["weight"] = "briggs"
imager_dict["clean_iterations"] = 1000
briggs_robust = 2,0,-2
prefix = imager_dict["imageprefix"]

for i, robust in enumerate(briggs_robust):
    imager_dict["msname"] = MS
    imager_dict["robust"] = robust
    imager_dict["imageprefix"] = "%s_robust-%d"%(prefix, i)
    pipeline.add("ares/imager", "imager_example_%d"%i, imager_dict, input=INPUT, output=OUTPUT, 
                 label="Imaging MS, robust=%f"%robust)


pipeline.run()
