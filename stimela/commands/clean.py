from stimela import logger, LOG_FILE, LOG_HOME, utils, CAB_USERNAME


def make_parser(subparsers):
    parser = subparsers.add_parser("clean", help='Convience tools for cleaning up after stimela')

    add = parser.add_argument

    add("-ai", "--all-images", action="store_true",
        help="Remove all images pulled/built by stimela. This include CAB images")

    add("-ab", "--all-base", action="store_true",
        help="Remove all base images")

    add("-ac", "--all-cabs", action="store_true",
        help="Remove all CAB images")

    add("-aC", "--all-containers", action="store_true",
        help="Stop and/or Remove all stimela containers")

    add("-bl", "--build-label", default=CAB_USERNAME,
        help="Label for cab images. All cab images will be named <CAB_LABEL>_<cab name>. The default is $USER")

    parser.set_defaults(func=clean)


def clean(args, conf):
    log = logger.StimelaLogger(LOG_FILE)
    log_cabs = logger.StimelaLogger('{0:s}/{1:s}_stimela_logfile.json'.format(LOG_HOME,
                                                                              args.build_label))

    if args.all_images:
        images = log.info['images'].keys()
        images = log_cabs.info['images'].keys()
        for image in images:
            utils.xrun('docker', ['rmi', image])
            log.remove('images', image)
            log.write()

        images = log_cabs.info['images'].keys()
        for image in images:
            if log_cabs.info['images'][image]['CAB']:
                utils.xrun('docker', ['rmi', image])
                log_cabs.remove('images', image)
                log_cabs.write()

    if args.all_base:
        images = list(log.info['images'].keys())
        for image in images:
            if log.info['images'][image]['CAB'] is False:
                utils.xrun('docker', ['rmi', image])
                log.remove('images', image)
                log.write()

    if args.all_cabs:
        images = list(log_cabs.info['images'].keys())
        for image in images:
            if log_cabs.info['images'][image]['CAB']:
                utils.xrun('docker', ['rmi', image])
                log_cabs.remove('images', image)
                log_cabs.write()

    if args.all_containers:
        containers = list(log.info['containers'].keys())
        for container in containers:
            cont = docker.Container(
                log.info['containers'][container]['IMAGE'], container)
            try:
                status = cont.info()['State']['Status'].lower()
            except:
                print('Could not inspect container {}. It probably doesn\'t exist, will remove it from log'.format(
                    container))
                status = "no there"

            if status == 'running':
                # Kill the container instead of stopping it, so that effect can be felt py parent process
                utils.xrun('docker', ['kill', container])
                cont.remove()
            elif status in ['exited', 'dead']:
                cont.remove()

            log.remove('containers', container)
            log.write()
