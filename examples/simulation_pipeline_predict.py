## Penthesilea examples
# In this example we show how to write a pipeline
# That predicts visiblities from a FITS image
# Sphesihle Makhathini <sphemakh@gmail.com>

from Otrera import otrera, utils, Container

input = "/home/makhathini/Penthesilea/input"
output = "/home/makhathini/Penthesilea/output"


## All  configuration files should be stored in the same place
configs_path = "../input/configs"
# These are the configs I'll need for this pipeline
simms_conf = "simms_params.json"
simulator_conf = "simulator_params.json"
imager_conf = "imager_params.json"

# The image must be place in Penthesilea/input/skymodels
imagename = "cygnusA.fits"

# start oterera instance
pipeline = otrera.Define("test_predict", configs_path)

## Make empty MS 
# When predicting from a FITS file
# simms container needs to know about the FITS image
simms_dict = utils.readJson(configs_path+"/"+simms_conf)
simms_dict["predict"] = True
simms_dict["skymodel"] = imagename

pipeline.add("penthesilea/simms", "simms", simms_dict,  input=input, output=output, 
             label="Creating empty MS")

## Simulate visibilities into MS
# Modify simulator_conf file to take a FITS file
predict_dict = utils.readJson(configs_path+"/"+simulator_conf)
predict_dict["skymodel"] = imagename
pipeline.add("penthesilea/predict", "predict", predict_dict, input=input, output=output,
             label="Predict visibilities from FITS image")

# To make things a bit more interesting,
# Lets also add a component model (point and/or gaussians) to the visibilites
simulator_dict = utils.readJson(configs_path+"/"+simulator_conf)
simulator_dict["skymodel"] = "nvss1deg.lsm.html"
simulator_dict["add_component_model"] = True
# Assume noise was added with FITS image
simulator_dict["addnoise"] = False
pipeline.add("penthesilea/simulator", "simulator", simulator_dict, input=input, output=output,
             label="Adding component model")

## Image
pipeline.add("penthesilea/imager", "imager", imager_conf, input=input, output=output,
             label="Imaging MS")


# Run pipeline. The containers above will be run in sequence
# I run this in a try/catch clause to ensure that I remove containers that I create
try:
    pipeline.run()
    # Clean up containers
    pipeline.rm()
    pipeline.log.info("Pipeline [%s] ran successfully."%pipeline.name)

except Container.DockerError:
    # Clean up containers
    pipeline.rm()
    raise Container.DockerError("A container failed to execute. Please check the logs")
