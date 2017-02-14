# 0.1.1

* Improve logging
* Add moresane
* Add CATTERY Path where needed



# 0.1.0

* Change package name from *Penthesilea* to *Stimela*
* Start using radioastro docker images
* Add lwimager, wslcean, casa imagers (instead of a single imager image)
* Add owlcat base image
* Add container, docker image, and job loging

# 0.2.5 
- Improve handling of ctrl+c. Send terminate
  signal to container.   
- Improve handling of FITS images when predicting
  visibilities; allow for minimal FITS images.  
- Add clean fuction to help clean up after stimela  
- Improve/Fx logging of images and containers

# 0.2.6
- Use correct package(stimel_misc) to get stimel version 

# 0.2.7
- Fix noise only simulation in simulator cab. Don not look for file if skymodel is None
- Allow user to specify gain matrix type in simulator   
- Make custom katdal base image
