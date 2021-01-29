from stimela import logger, LOG_FILE, BASE


def make_parser(subparsers):

    parser = subparsers.add_parser('build', help='Build stimela base images')

    parser.add_argument("images", nargs="*", type=str, metavar="IMAGE[:VERSION]", 
                        help="image/version to build (builds all versions by default)")
    
    parser.add_argument("-a", "--all", action="store_true", help="build all unavailable images (all images, in combination with --rebuild)")

    parser.add_argument("-r", "--rebuild", action="store_true", help="force rebuild of image(s)")

    # parser.add_argument("-b", "--base", action="store_true",
    #                     help="Build base images")

    # parser.add_argument("-c", "--cab", metavar="CAB,CAB_DIR",
    #                     help="Executor image (name) name, location of executor image files")

    # parser.add_argument("-uo", "--us-only",
    #                     help="Only build these cabs. Comma separated cab names")

    # parser.add_argument("-i", "--ignore-cabs", default="",
    #                     help="Comma separated cabs (executor images) to ignore.")
    
    # parser.add_argument("-p", "--podman", action="store_true", help="Build images using podman.")

    # parser.add_argument("-nc", "--no-cache", action="store_true",
    #                     help="Do not use cache when building the image")

    parser.set_defaults(func=build)


def build(args, conf):
    from stimela.main import BACKEND, log

    available_images = BACKEND.available_images()
    build_images = args.images
    if args.all:
        build_images = conf.base.keys()
    else:
        build_images = args.images

    if not build_images:
        log.info("No images specified. Run 'stimela build -h' for help.")
        return 0

    for imagename in build_images:
        if ':' in imagename:
            imagename, version = imagename.split(":", 1)
        else:
            version = None

        if imagename not in conf.base:
            log.error(f"base image '{imagename}' is not known to Stimela")
            return 2

        image = conf.base[imagename]

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
                if not args.rebuild:
                    log.info(f"image '{imagename}:{version}' already exists, skipping")
                    continue

            BACKEND.build(image, version)



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
