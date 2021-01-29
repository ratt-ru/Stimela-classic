from stimela import logger, LOG_FILE, BASE, utils
from stimela.backends import docker, singularity, podman


def make_parser(subparsers):
    parser = subparsers.add_parser("kill", help='Gracefully kill stimela process(s).')

    add = parser.add_argument

    add("pid", nargs="*", help="Process ID")

    parser.set_defaults(func=kill)


def kill(args, conf):
    log = logger.StimelaLogger(LOG_FILE)

    for pid in args.pid:

        found = pid in log.info['processes'].keys()

        if not found:
            print("Could not find process {0}".format(pid))
            continue

        try:
            os.kill(int(pid), signal.SIGINT)
        except OSError:
            raise OSError(
                'Process with PID {} could not be killed'.format(pid))

        log.remove('processes', pid)
    log.write()

