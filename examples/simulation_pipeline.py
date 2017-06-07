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
pipeline.add("cab/simms",                   # Executor image to start container from 
             "simms_example",               # Container name
             { # Parameters to parse to executor container
                "msname"    :   MS,                     
                "telescope" :   "meerkat",              # Telescope name
                "direction" :   "J2000,0deg,-30deg",    # Phase tracking centre of observation
                "synthesis" :   0.128,                  # Synthesis time of observation
                "dtime"     :   10,                      # Integration time in seconds
                "freq0"     :   "750MHz",               # Start frequency of observation
                "dfreq"     :   "1MHz",                 # Channel width
                "nchan"     :   1                       # Number of channels
             },
             input=INPUT,                               # Input folder
             output=OUTPUT,                             # Output folder
             label="Creating MS")                       # Process label


# 2: Simulate visibilities into it
pipeline.add("cab/simulator", 
             "simulator_example",
             {
                "msname"    :   MS,
                "skymodel"  :   LSM,                    # Sky model to simulate into MS
                "addnoise"  :   True,                   # Add thermal noise to visibilities
                "column"    :   "CORRECTED_DATA",       # Simulated data will be saved in this column
                "sefd"      :   831,                    # Compute noise from this SEFD
                "recenter"  :   True                    # Recentre sky model to phase tracking centre of MS
             },
            input=INPUT, output=OUTPUT,
            label="Simulating visibilities")


pipeline.add('cab/casa_plotms', 
            'plot_vis',
            {
                "vis"           :   MS,
                "xaxis"         :   'uvdist',
                "yaxis"         :   'amp',
                "xdatacolumn"   :   'corrected',
                "ydatacolumn"   :   'corrected',
                "plotfile"      :   PREFIX+'-amp_uvdist.png',
                "overwrite"     :   True,
            },
            input=INPUT,
            output=OUTPUT,
            label='plot_amp_uvdist:: Plot amplitude vs uv-distance')

## 3: Image
# Make things a bit interesting by imaging with different weights 
# Briggs robust values to use for each image
briggs_robust = 2, 0, -2

for i, robust in enumerate(briggs_robust):

    pipeline.add("cab/wsclean",
                 "imager_example_robust_{:d}".format(i), 
                 {
                    "msname"            :   MS,
                    "weight"            :   "briggs {:d}".format(i),
                    "prefix"            :   "{:s}_robust-{:d}".format(PREFIX, robust),
                    "npix"              :   2048,                   # Image size in pixels
                    "cellsize"          :   2,                      # Size of each square pixel
                    "clean_iterations"  :   1000,                   # Perform 1000 iterarions of clean (Deconvolution)
                 },
                 input=INPUT, 
                 output=OUTPUT, 
                 label="Imaging MS, robust={:d}".format(robust))

# Run recipe. The 'steps' added above will be executed in the sequence that they were adde. The 'steps' added above will be
# executed in the sequence that they were added
pipeline.run()
