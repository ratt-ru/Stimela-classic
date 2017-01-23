# import stimela package
import stimela

# Recipe I/O configuration
INPUT = "input" # This folder must exist
OUTPUT = "output"
MSDIR = "msdir"
PREFIX = "stimela-example"  # Prefix for output images

# MS name
MS = "meerkat_simulation_example.ms"

# Use the NVSS skymodel. This is natively available
LSM = "nvss1deg.lsm.html"


# Start stimela Recipe instance
pipeline = stimela.Recipe("Simulation Example",     # Recipe name
                  ms_dir=MSDIR)             # Folder in which to find MSs

 # 1: Make empty MS 
simms_dict = {
    "msname"   :   MS,                     
    "telescope" :   "meerkat",              # Telescope name
    "direction" :   "J2000,0deg,-30deg",   # Phase tracking centre of observation
    "synthesis" :   0.125,                      # Synthesis time of observation
    "dtime"     :   30,                      # Exposure time
    "freq0"     :   "750MHz",               # Start frequency of observation
    "dfreq"     :   "1MHz",                 # Channel width
    "nchan"     :   1                      # Number of channels
    }

pipeline.add("cab/simms",                   # Executor image to start container from 
             "simms_example",               # Container name
             simms_dict,                    # Parameters to parse to executor container
             input=INPUT,                   # Input folder
             output=OUTPUT,                 # Output folder
             label="Creating MS")           # Process label


 # 2: Simulate visibilities into it
simulator_dict = {
    "msname"    :   MS,
    "skymodel"  :   LSM,                    # Sky model to simulate into MS
    "addnoise"  :   True,                   # Add thermal noise to visibilities
    "column"    :   "CORRECTED_DATA",
    "sefd"      :   831,                    # Compute noise from this SEFD
    "recenter"  :   True                    # Recentre sky model to phase tracking centre of MS
    }

pipeline.add("cab/simulator", 
             "simulator_example",
              simulator_dict, 
              input=INPUT, output=OUTPUT,
              label="Simulating visibilities")


## 3: Image
# Make things a bit interesting by imaging with different weights 
imager_dict = {
    "msname"    :   MS,
    "npix"      :   2048,                   # Image size in pixels
    "cellsize"  :   2,                      # Size of each square pixel
    "clean_iterations"  :   1000            # Perform 1000 iterarions of clean (Deconvolution)
    }

# Briggs robust values to use for each image
briggs_robust = 2, 0, -2

for i, robust in enumerate(briggs_robust):

    imager_dict["weight"] = "briggs {:f}".format(robust) # update Briggs robust parameter
    imager_dict["prefix"] = "{:s}_robust-{:f}".format(PREFIX, robust) # Prefix for output images

    pipeline.add("cab/wsclean",
                 "imager_example_robust_{:f}".format(robust), 
                 imager_dict, 
                 input=INPUT, 
                 output=OUTPUT, 
                 label="Imaging MS, robust={:f}".format(robust))

# Run recipe. The 'steps' added above will be executed in the sequence that they were adde. The 'steps' added above will be
# executed in the sequence that they were added
pipeline.run()
