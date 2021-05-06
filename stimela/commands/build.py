import click
from typing import List
from stimela.main import cli
import stimela


@cli.command(
    help="""(Re)build stimela base images. Specify a list of image names and versions (if a version is omitted, builds all known versions of image),
            or else use --all to build all required base images. 
         """,
    short_help="build stimela base images",
    no_args_is_help=True)
@click.argument("images", nargs=-1, metavar="NAME[:VERSION]", required=False) 
#                help="image/version to build (builds all versions of image by default)")
@click.option("-a", "--all", is_flag=True, 
                help="build all unavailable images (all images, in combination with --rebuild)")
@click.option("-r", "--rebuild", is_flag=True, 
                help="force rebuild of image(s)")
def build(images: List[str], all=False, rebuild=False):
    from stimela.main import BACKEND
    from stimela import CONFIG
    log = stimela.logger()

    available_images = BACKEND.available_images()
    if all:
        build_images = CONFIG.base.keys()
    else:
        build_images = images

    if not build_images:
        log.info("No images specified. Run 'stimela build -h' for help.")
        return 0

    for imagename in build_images:
        if ':' in imagename:
            imagename, version = imagename.split(":", 1)
        else:
            version = None

        if imagename not in CONFIG.base:
            log.error(f"base image '{imagename}' is not known to Stimela")
            return 2

        image = CONFIG.base[imagename]

        if version is None:
            build_versions = image.images.keys()
        elif version in image.images:
            build_versions = [version]
        else:
            log.error(f"version '{version}' is not defined for base image '{imagename}'")
            return 2

        # now loop over build versions
        for version in build_versions:
            
            # check if already exists
            if imagename in available_images and version in available_images[imagename]:
                if not rebuild:
                    log.info(f"image '{imagename}:{version}' already exists, skipping")
                    continue

            BACKEND.build(image, version)
