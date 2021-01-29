from stimela import LOG_FILE, BASE, utils


def make_parser(subparsers):
    parser = subparsers.add_parser("images", help='List all stimela base images.')

    parser.add_argument("-i", "--print-ids", action="store_true",
                        help="list in more terse image+ID format")

    parser.set_defaults(func=images)


def images(args, conf):
    from stimela.main import BACKEND, log

    available = BACKEND.available_images()

    if not args.print_ids:
        log.info("image list follows")

        header = f"{'IMAGE':19} {'VERSION':19} {'DESCRIPTION':19} BUILT BY"
        print(header)
        print("-"*len(header))

    for _, baseinfo in conf.base.items():
        name0 = name = baseinfo.name
        for version, versinfo in baseinfo.images.items():
            if name0 in available and version in available[name0]:
                image = available[name0][version]
                status = f"{image.build.user}@{image.build.host} on {image.build.date} using stimela {image.build.stimela_version}"
            else:
                image = None
                status = "not found: please pull or build" 
            if args.print_ids:
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






## old implementation

# def images(args, conf):

#     log = logger.StimelaLogger(LOG_FILE)
#     log.display('images')

#     if args.clear:
#         log.clear('images')
#         log.write()


