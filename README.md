# Penthesilea

Tools for flexible and system independent (as much docker allows) radio interferometric simulations and reductions.
The main goal of this project is to test the feasibilty of using the AWS system to do SKA1-MID scale simulations and reductions. The simulations and reduction framework is largely based on [Pyxis](https://github.com/ska-sa/pyxis) and [Docker](https://www.docker.com/).

The docker images for this project can be found at: https://hub.docker.com/u/penthesilea

This project is funded by the [SKA/AWS Astrocompute in the cloud ](https://www.skatelescope.org/ska-aws-astrocompute-call-for-proposals) initiative. 


## Requires 
* Docker
* Python

## Running the pipeline

* **Step 1:** Download the repository 
```
git clone https://github.com/SpheMakh/Penthesilea.git && cd Penthesilea
```

* **Step 2:** Build/Download required images
  * Build: `make build` or
  * Download: `make pull`

* **Step 3:** Define you simulation. You can set the parameters of your simulation via a *JSON* config file. 
  The default configuration is at `input/configs/driver.json`. Your customised configuration should also be place in the same folder. **Do not modify the default config**, make a copy then then modify that copy. If you are using a custom sky model, please place it in `input/skymodels`. See available telecopes and sky models in tables at bottom of this page. 

* **Step 4:** Once the images are built/downloaded. You can start the pipeline by running 
```
make run config=<json config file>
```
If `config` is not specified, the pipeline will proceed with the default configuration. **Only specify the name of your custom configuration and not the path**

After the pipeline is done, your output products will be placed in `output`.

## Stop/kill
You can stop/kill running penthesilia containers by running `make stop` or `make kill`. 

## Telescopes
| Key | Array |    
| ------|-----| 
|ska197|SKA1MID 197 dishes|
|ska254|SKA1MID 254 dishes|  
|meerkat|MeerKAT|  
|kat-7|KAT-7|  
|jvla-a|JVLA A Config|  
|jvla-b|JVLA B Config|  
|jvla-c|JVLA C Config|    
|jvla-d|JVLA D Config|  
|wsrt|WSRT|  

## Sky models
| Key | Array |    
| ------|-----| 
|nvss1deg |1 sq deg field from the  NVSS catalogue|
|scubed1deg|1 sq degree field from the S-cubed simulation|  
|cosmos| field from JVLA COSMOS cataloge|  
|ecdfs| field from JVLA ECDFS catalogue|  
|xmm-lss|field from JVLA XMM-LSS catalogue|  
