import click
from typing import List
from stimela.main import cli, StimelaContext, pass_stimela_context


@cli.command(
    help="""Push stimela base images. Specify a list of image names and versions (if a version is omitted, pushes all known versions of image),
            or else use --all to push everything. 
         """,
    short_help="push stimela images to registry",
    no_args_is_help=True)
@click.argument("images", nargs=-1, metavar="NAME[:VERSION]", required=False) 
@click.option("-a", "--all", is_flag=True, 
                help="push all images")
@pass_stimela_context
def push(context: StimelaContext, images: List[str], all=False):

    available_images = context.backend.available_images()
    push_images = context.config.base.keys() if all else images

    for imagename in push_images:
        if ':' in imagename:
            imagename, version = imagename.split(":", 1)
        else:
            version = None

        if imagename not in context.config.base:
            context.log.error(f"base image '{imagename}' is not known to Stimela")
            return 2

        image = context.config.base[imagename]

        if version is None:
            push_versions = image.images.keys()
        elif version in image.images:
            push_versions = [version]
        else:
            context.log.error(f"version '{version}' is not defined for base image '{imagename}'")
            return 2

        # now loop over push versions
        for version in push_versions:
            # check if already exists
            if imagename not in available_images or version not in available_images[imagename] \
                        or available_images[imagename][version].build is None:
                context.log.warning(f"image '{imagename}:{version}' not found, has it been built?")
                continue

            context.backend.push(image, version)


