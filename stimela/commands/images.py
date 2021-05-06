import click
import stimela
from stimela.main import cli


@cli.command(
    help="""Lists all known stimela images. 
         """,
    short_help="list known stimela images")
@click.option("-i", "--print-ids", is_flag=True, 
                help="list in the more terse image+ID format.")
def images(print_ids=False):
    from stimela.main import BACKEND
    log = stimela.logger()
    available = BACKEND.available_images()

    if not print_ids:
        log.info("image list follows")

        header = f"{'IMAGE':19} {'VERSION':19} {'DESCRIPTION':19} BUILT BY"
        print(header)
        print("-"*len(header))

    for _, baseinfo in context.config.base.items():
        name0 = name = baseinfo.name
        for version, versinfo in baseinfo.images.items():
            if name0 in available and version in available[name0]:
                image = available[name0][version]
                status = f"{image.build.user}@{image.build.host} on {image.build.date} using stimela {image.build.stimela_version}"
            else:
                image = None
                status = "not found: please pull or build" 
            if print_ids:
                if image is None:
                    print(f"{name:19} ???")
                else:
                    iid = image.iid
                    if iid.startswith("sha256:"):
                        iid = iid.split(":", 1)[1]
                    if len(iid) > 12:
                        iid = iid[:12]
                    print(f"{name:19} {image.full_name:39} {iid}")
            else:
                print(f"{name:19} {version:19} {versinfo.info:19} {status}")
                name = ''
