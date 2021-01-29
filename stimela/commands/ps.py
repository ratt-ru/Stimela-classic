from stimela import logger, LOG_FILE, BASE, utils

from stimela.backends import docker, singularity, podman

def make_parser(subparsers):
    parser = subparsers.add_parser("ps", help='List all running stimela processes')

    add = parser.add_argument

    add("-c", "--clear", action="store_true",
        help="Clear logfile that keeps track of stimela processes. This doesn't do anything ot the processes themselves.")

    parser.set_defaults(func=ps)


def ps(args, conf):

    log = logger.StimelaLogger(LOG_FILE)
    log.display('processes')
    if args.clear:
        log.clear('processes')
        log.write()

