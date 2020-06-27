# import stimela package
import stimela
import os

# Recipe I/O configuration
INPUT = "input"  # This folder must exist
OUTPUT = "output"
MSDIR = "msdir"
PREFIX = "stimela-example"  # Prefix for output images
try:
    SINGULARTITY_IMAGE_DIR = os.environ["STIMELA_SINGULARTITY_IMAGE_DIR"]
except KeyError:
    SINGULARTITY_IMAGE_DIR = None

# MS name
MS = "meerkat_simulation_example.ms"

# Use the NVSS skymodel. This is natively available
LSM = "nvss1deg.lsm.html"

# Start stimela Recipe instance
pipeline = stimela.Recipe("Simulation Example",     # Recipe name
                          ms_dir=MSDIR,
                          indir=INPUT,
                          outdir=OUTPUT,
                          singularity_image_dir=SINGULARTITY_IMAGE_DIR,
                          log_dir=os.path.join(OUTPUT, "logs"),
                          )

#pipeline.JOB_TYPE = "docker"

# 1: Make empty MS
pipeline.add("cab/simms",                   # Executor image to start container from
             "simms_example",               # Container name
             {  # Parameters to parse to executor container
                "msname":   MS,
                "telescope":   "meerkat",              # Telescope name
                "direction":   "J2000,0deg,-30deg",    # Phase tracking centre of observation
                "synthesis":   0.128,                  # Synthesis time of observation
                "dtime":   10,                      # Integration time in seconds
                "freq0":   "750MHz",               # Start frequency of observation
                "dfreq":   "1MHz",                 # Channel width
                "nchan":   1                       # Number of channels
             },
             label="Creating MS",                       # Process label
             cpus=2.5,
             memory_limit="2gb")

pipeline.add("cab/casa_listobs", "obsinfo",
        {
            "vis" : MS,
            "listfile" : MS + "-obsinfo.txt",
            "overwrite": True,
            }, 
        label="obsinfo:: Observation information")

# 2: Simulate visibilities into it
pipeline.add("cab/simulator",
             "simulator_example",
             {
                 "msname":   MS,
                 "skymodel":   LSM,                    # Sky model to simulate into MS
                 "addnoise":   True,                   # Add thermal noise to visibilities
                 "column":   "DATA",
                 "Gjones": True, # Simulated data will be saved in this column
                 "sefd":   831,                    # Compute noise from this SEFD
                 # Recentre sky model to phase tracking centre of MS
                 "tile-size": 64,
                 "threads": 4,
             },
             label="Simulating visibilities")

pipeline.add("cab/calibrator",
             "cal_example",
             {
                 "msname":   MS,
                 "skymodel":   LSM,
                 "tile-size": 64,
                 "threads": 4,
             },
             label="Calibrating visibilities")



# 3: Image
# Make things a bit interesting by imaging with different weights
# Briggs robust values to use for each image
briggs_robust = 2, 0, -2

for i, robust in enumerate(briggs_robust):

    pipeline.add("cab/wsclean",
                 "imager_example_robust_{:d}".format(i),
                 {
                     "msname":   MS,
                     "weight":   "briggs {:d}".format(robust),
                     "prefix":   "{:s}_robust-{:d}".format(PREFIX, robust),
                     "npix":   2048,                   # Image size in pixels
                     "scale":   2,                      # Size of each square pixel
                     # Perform 1000 iterarions of clean (Deconvolution)
                     "niter":   1000,
                     "pol" : "I",
                     "multiscale": True,
                     "multiscale-scales" : [0,2],
                 },
                 label="Imaging MS, robust={:d}".format(robust),
                 cpus=2,
                 memory_limit="2gb")

pipeline.add("cab/casa_rmtables", "delete_ms", {
    "tablenames": MS + ":msfile",
},
    label="Remove MS")
# Run recipe. The 'steps' added above will be executed in the sequence that they were adde. The 'steps' added above will be
# executed in the sequence that they were added
pipeline.run()
