from Otrera import otrera, utils, Container

input = "/home/makhathini/Penthesilea/input"
output = "/home/makhathini/Penthesilea/output"


## All  configuration files should be stored in the same place
configs_path = "../input/configs"
# These are the names
simms_conf = "simms_params.json"
simulator_conf = "simulator_params.json"
sourcery_conf = "sourcery_params.json"
calibrator_conf = "calibrator_params.json"
imager_conf = "imager_params.json"

msname = "penthesilea_default.MS"


# start oterera instance
pipeline = otrera.Define("test", configs_path)

# Make empty MS 
#pipeline.add("penthesilea/simms", "simms", simms_conf, input=input, output=output, 
#             label="Creating MS")

# Simulate visibilities into it
# enable G-Jones first
simulator_dict = utils.readJson(configs_path+"/"+simulator_conf)
simulator_dict["G_jones"] = True
#pipeline.add("penthesilea/simulator", "simulator", simulator_dict, input=input, output=output,
#             label="Simulating visibilities")

# Image Data (to make calibration model)
imager_dict = utils.readJson(configs_path+"/"+imager_conf)
imager_dict["psf"] = True
imager_dict["npix"] = 2048
#pipeline.add("penthesilea/imager", "imager_cal_model", imager_dict, input=input, output=output, 
#                 label="Imaging MS. Make cal. model")

# Run source finder
imageprefix = imager_dict["imageprefix"]
sourcery_dict = utils.readJson(configs_path+"/"+sourcery_conf)
sourcery_dict["imagename"] = "%s-%s.restored.fits"%(imageprefix, imager_dict["imager"])
sourcery_dict["psf"] = "%s-%s.psf.fits"%(imageprefix, imager_dict["imager"])
sourcery_dict["prefix"] = imageprefix

pipeline.add("penthesilea/sourcery", "sourcery", sourcery_dict, input=input, output=output,
             label="Running Source finder. Making Cal model")

# Calibrate data
calibrator_dict = utils.readJson(configs_path+"/"+calibrator_conf)
calibrator_dict["skymodel"] = sourcery_dict["imagename"].replace(".fits", "_positive.lsm.html")
calibrator_dict["msname"] = msname
pipeline.add("penthesilea/calibrator", "calibrator", calibrator_dict, input=input, output=output,
             label="Calibrating data (G-Jones)")

## Image
imager_dict = utils.readJson(configs_path+"/"+imager_conf)
imager_dict["imageprefix"] = imageprefix+"-corr_res"
pipeline.add("penthesilea/imager", "imager_final", imager_dict, input=input, output=output, 
                 label="Imaging MS")


# Run pipeline. The containers above will be run in sequence
try:
    pipeline.run()
    # Clean up containers
    pipeline.rm()

except Container.DockerError:
    # Clean up containers
    pipeline.rm()
    raise Container.DockerError("A container failed to execute. Please check the logs")
