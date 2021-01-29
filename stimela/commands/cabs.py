from stimela.main import get_cab_definition
from stimela import logger, LOG_HOME, CAB_USERNAME, CAB_PATH


def make_parser(subparsers):
    parser = subparsers.add_parser("cabs", help='List executor (a.k.a cab) images')

    parser.add_argument("-l", "--list", action="store_true",
                        help="List cab names")

    parser.add_argument("-i", "--cab-doc",
                        help="Will display document about the specified cab. For example, \
to get help on the 'cleanmask cab' run 'stimela cabs --cab-doc cleanmask'")

    parser.add_argument("-ls", "--list-summary", action="store_true",
                        help="List cabs with a summary of the cab")

    parser.set_defaults(func=cabs)


def cabs(args, conf):
    logfile = '{0:s}/{1:s}_stimela_logfile.json'.format(
        LOG_HOME, CAB_USERNAME)

    from stimela.main import get_cab_definition

    if args.cab_doc:
        name = '{0:s}_cab/{1:s}'.format(CAB_USERNAME, args.cab_doc)
        cabdir = "{:s}/{:s}".format(CAB_PATH, args.cab_doc)
        get_cab_definition(cabdir)

    elif args.list_summary:
        for val in CAB:
            cabdir = "{:s}/{:s}".format(CAB_PATH, val)
            try:
                get_cab_definition(cabdir, header=True)
            except IOError:
                pass
    else:
        print(', '.join(CAB))


# docker images --format "{{json .ID}} {{json .Repository}} {{json .Tag}}"

## singularity:
# singularity inspect -l --json ubuntu.img

## podman:
# 