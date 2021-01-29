from stimela import logger, LOG_FILE, BASE


def make_parser(subparsers):

    parser = subparsers.add_parser('push', help='Push stimela base images to registry')

    parser.add_argument("images", nargs="*", type=str, metavar="IMAGE[:VERSION]", 
                        help="image/version to push (pushes all versions by default)")
    
    parser.add_argument("-a", "--all", action="store_true", help="push all images")

    parser.set_defaults(func=push)


def push(args, conf):
    from stimela.main import BACKEND, log

    available_images = BACKEND.available_images()
    push_images = args.images
    if args.all:
        push_images = conf.base.keys()
    else:
        push_images = args.images

    if not push_images:
        log.info("No images specified. Run 'stimela push -h' for help.")
        return 0

    for imagename in push_images:
        if ':' in imagename:
            imagename, version = imagename.split(":", 1)
        else:
            version = None

        if imagename not in conf.base:
            log.error(f"base image '{imagename}' is not known to Stimela")
            return 2

        image = conf.base[imagename]

        if version is None:
            push_versions = image.images.keys()
        elif version in image.images:
            push_versions = [version]
        else:
            log.error(f"version '{version}' is not defined for base image '{imagename}'")
            return 2

        # now loop over build versions
        for version in push_versions:
            # check if already exists
            if imagename not in available_images or version not in available_images[imagename] \
                        or available_images[imagename][version].build is None:
                log.warning(f"image '{imagename}:{version}' not found, has it been built?")
                continue

            BACKEND.push(image, version)


    # jtype = "podman" if args.podman else "docker"
    # log = logger.StimelaLogger(LOG_FILE, jtype=jtype)

    # no_cache = ["--no-cache"] if args.no_cache else []

    # if args.cab:
    #     raise SystemExit("DEPRECATION NOTICE: This feature has been deprecated. Please specify your \
    #             custom cab via the 'cabpath' option of the Recipe.add() function.")

    # if args.base:
    #     # Build base and meqtrees images first
    #     BASE.remove("base")
    #     BASE.remove("meqtrees")
    #     BASE.remove("casa")
    #     BASE.remove("astropy")

    #     for image in ["base", "meqtrees", "casa", "astropy"] + BASE:
    #         dockerfile = "{:s}/{:s}".format(stimela.BASE_PATH, image)
    #         image = "stimela/{0}:{1}".format(image, stimela.__version__)
    #         __call__(jytpe).build(image,
    #                      dockerfile, args=no_cache)

    #     log.log_image(image, dockerfile, replace=True)
    #     log.write()

    #     return 0
    # raise SystemExit("DEPRECATION NOTICE: The building of cab images has been deprecated")
