from otrera import Pipeline
import os

INPUT = "input"
OUTPUT = "output"
DATA = "../data"
MSDIR = "msdir"


## All  configuration files should be stored in the same place
CONFIGS = "../data/configs"
# These are the names
simms_template = "simms_params.json"
simulator_template = "simulator_params.json"
imager_template = "imager_params.json"

msname = "meerkat_simulation_example.ms"


# start oterera instance
pipeline = Pipeline("Simulation Example", CONFIGS, data=DATA, ms_dir=MSDIR)

# Make empty MS 
simms_dict = pipeline.readJson(simms_template)
simms_dict["msname"] = msname
pipeline.add("ares/simms", "simms_example", simms_dict, input=INPUT, output=OUTPUT, 
             label="Creating MS")

# Simulate visibilities into it
simulator_dict = pipeline.readJson(simulator_template)
simulator_dict["msname"] = msname
pipeline.add("ares/simulator", "simulator_example", simulator_dict, input=INPUT, output=OUTPUT,
             label="Simulating visibilities")

## Image
# This is an example of how to iterate over a variable
# I want to make images with different uv-weights 

imager_dict = pipeline.readJson(imager_template)
imager_dict["weight"] = "briggs"
briggs_robust = 2,0,-2
prefix = imager_dict["imageprefix"]

for i, robust in enumerate(briggs_robust):
    imager_dict["msname"] = msname
    imager_dict["robust"] = robust
    imager_dict["imagename"] = "%s_robust-%d"%(prefix, i)
    pipeline.add("ares/imager", "imager_example_%d"%i, imager_dict, input=INPUT, output=OUTPUT, 
                 label="Imaging MS, robust=%f"%robust)


pipeline.run()
