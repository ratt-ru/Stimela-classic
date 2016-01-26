from stimela import Recipe

INPUT = "input"
OUTPUT = "output"
MSDIR = "msdir"

MS = "meerkat_simulation_example.ms"
LSM = "nvss1deg.lsm.html"


# start oterera instance
pipeline = Recipe("Simulation Example", ms_dir=MSDIR)

## 1: Make empty MS 
simms_dict = {}
simms_dict["msname"] = MS
simms_dict["telescope"] = "meerkat"
simms_dict["synthesis"] = 1
simms_dict["direction"] = "J2000,90deg,-45deg"
simms_dict["dtime"] = 10
simms_dict["freq0"] = "750MHz"
simms_dict["dfreq"] = "1MHz"
simms_dict["nchan"] = 10
pipeline.add("cab/simms", "simms_example", simms_dict, input=INPUT, output=OUTPUT, 
             label="Creating MS")


## 2: Simulate visibilities into it
simulator_dict = {}
simulator_dict["msname"] = MS
simulator_dict["addnoise"] = True
simulator_dict["sefd"] = 831
simulator_dict["skymodel"] = LSM
pipeline.add("cab/simulator", "simulator_example", simulator_dict, input=INPUT, output=OUTPUT,
             label="Simulating visibilities")


## 3: Image
# Make things a bit interesting by imaging with different weights 
imager_dict = {}
imager_dict["weight"] = "briggs"
#imager_dict["imager"] = "casa"
imager_dict["clean_iterations"] = 1000
briggs_robust = [2] #, 0, -2
prefix = "stimela-example"

for i, robust in enumerate(briggs_robust):
    imager_dict["msname"] = MS
    imager_dict["robust"] = robust
    imager_dict["imageprefix"] = "%s_robust-%d"%(prefix, i)
    pipeline.add("cab/casa", "imager_example_%d"%i, imager_dict, input=INPUT, output=OUTPUT, 
                 label="Imaging MS, robust=%f"%robust)

pipeline.run(steps=[3])
