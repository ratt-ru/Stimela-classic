from Otrera import otrera, utils

input = "/home/makhathini/Penthesilea/input"
output = "/home/makhathini/Penthesilea/output"


## All  configuration files should be stored in the same place
configs_path = "../input/configs"
# These are the names
simms_conf = "simms_params.json"
simulator_conf = "simulator_params.json"
imager_conf = "imager_params.json"


# start oterera instance
pipeline = otrera.Define("test", configs_path)

# Make empty MS 
pipeline.add("penthesilea/simms", "simms", simms_conf, input=input, output=output, 
             label="Creating MS")
# Simulate visibilities into it
pipeline.add("penthesilea/simulator", "simulator", simulator_conf, input=input, output=output,
             label="Simulating visibilities")

## Image
# This is an example of how to iterate over a variable
# I want to make images with different uv-weights 

imager_dict = utils.readJson(configs_path+"/"+imager_conf)
imager_dict["weight"] = "briggs"
briggs_robust = 2,0,-2
prefix = imager_dict["imageprefix"]

for i, robust in enumerate(briggs_robust):
    imager_dict["robust"] = robust
    imager_dict["imagename"] = "%s_robust-%d"%(prefix, i)
    pipeline.add("penthesilea/imager", "imager_%d"%i, imager_dict, input=input, output=output, 
                 label="Imaging MS, robust=%f"%i)


# Run pipeline. The containers above will be run in sequence
try:
    pipeline.run()
    # Clean up containers
    pipeline.rm()

except Container.DockerError:
    # Clean up containers
    pipeline.rm()
    raise Container.DockerError("A container failed to execute. Please check the logs")
