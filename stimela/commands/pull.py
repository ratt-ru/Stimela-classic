from stimela import logger, LOG_FILE, BASE,  utils
from stimela.backends import docker, singularity, podman


def make_parser(subparsers):

    parser = subparsers.add_parser('pull', help='Pull docker stimela base images')

    add = parser.add_argument

    add("-im", "--image", nargs="+", metavar="IMAGE[:TAG]",
        help="Pull base image along with its tag (or version). Can be called multiple times")

    add("-f", "--force", action="store_true",
        help="force pull if image already exists")

    add("-s", "--singularity", action="store_true",
        help="Pull base images using singularity."
        "Images will be pulled into the directory specified by the enviroment varaible, STIMELA_PULLFOLDER. $PWD by default")

    add("-d", "--docker", action="store_true",
        help="Pull base images using docker.")

    add("-p", "--podman", action="store_true",
        help="Pull base images using podman.")

    add("-cb", "--cab-base", nargs="+",
        help="Pull base image for specified cab")

    add("-pf", "--pull-folder",
        help="Images will be placed in this folder. Else, if the environmnental variable 'STIMELA_PULLFOLDER' is set, then images will be placed there. "
        "Else, images will be placed in the current directory")

    parser.set_defaults(func=pull)


def pull(args, conf):

    if args.pull_folder:
        pull_folder = args.pull_folder
    else:
        try:
            pull_folder = os.environ["STIMELA_PULLFOLDER"]
        except KeyError:
            pull_folder = "."

    if args.podman:
        jtype = "podman"
    elif args.singularity:
        jtype = "singularity"
    elif args.docker:
        jtype = "docker"
    else:
        jtype = "docker"


    log = logger.StimelaLogger(LOG_FILE, jtype=jtype)
    images = log.read()['images']

    images_ = []
    for cab in args.cab_base or []:
        if cab in CAB:
            filename = "/".join([stimela.CAB_PATH, cab, "parameters.json"])
            param = utils.readJson(filename)
            tags = param["tag"]
            if not isinstance(tags, list):
                tags = [tags]
            for tag in tags:
                images_.append(":".join([param["base"], tag]))

    args.image = images_ or args.image
    if args.image:
        for image in args.image:
            simage = image.replace("/", "_")
            simage = simage.replace(":", "_") + singularity.suffix
            if args.singularity:
                singularity.pull(
                    image, simage, directory=pull_folder, force=args.force)
            elif args.docker:
                docker.pull(image)
                log.log_image(image, 'pulled')
            elif args.podman:
                podman.pull(image)
                log.log_image(image, 'pulled')
            else:
                docker.pull(image)
                log.log_image(image, 'pulled')
    else:
        base = []
        for cab_ in CAB:
            cabdir = "{:s}/{:s}".format(stimela.CAB_PATH, cab_)
            _cab = info(cabdir, display=False)
            tags = _cab.tag
            if not isinstance(tags, list):
                tags = [tags]
            for tag in tags:
                base.append(f"{_cab.base}:{tag}")
        base = set(base)

        for image in base:
            if args.singularity:
                simage = image.replace("/", "_")
                simage = simage.replace(":", "_") + singularity.suffix
                singularity.pull(
                    image, simage, directory=pull_folder, force=args.force)
            elif args.docker:
                docker.pull(image, force=args.force)
                log.log_image(image, 'pulled')
            elif args.podman:
                podman.pull(image, force=args.force)
                log.log_image(image, 'pulled')
            else:
                docker.pull(image, force=args.force)
                log.log_image(image, 'pulled')

    log.write()

