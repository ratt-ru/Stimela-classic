import os.path

from omegaconf.omegaconf import OmegaConf
import stimela
from datetime import datetime
from stimela import LOG_FILE, BASE
from enum import Enum

def make_parser(subparsers):

    parser = subparsers.add_parser('config', help='Adjust configuration settings')

    parser.add_argument("keys", nargs="*", type=str, metavar="KEY=VALUE", 
                        help="configuration settings to adjust")
    
    parser.add_argument("-s", "--save", action="store_true", help="saves config file even if nothing is changed")

    parser.set_defaults(func=save_config)


def save_config(args, conf):
    from stimela.main import log
    from stimela.config import CONFIG_FILE

    if os.path.exists(CONFIG_FILE):
        log.info(f"configuration file is {CONFIG_FILE}")
    else:
        log.info(f"configuration file {CONFIG_FILE} doesn't exist, using defaults")

    # print config, if no key=value args specified
    if not args.keys:
        for key, value in conf.opts.items():
            if isinstance(value, Enum):
                value = value.name
            print(f"    {key} = {value}")

    # change config, if key=value args specified
    for keyvalue in args.keys:
        if "=" not in keyvalue:
            log.error(f"invalid config setting '{keyvalue}', KEY=VALUE expected")
            return 2
        key, value = keyvalue.split("=", 1)
        if key not in conf.opts:
            log.error(f"unknown config key '{key}'")
            return 2
        conf.opts[key] = value
        print(f"    setting {key} = {value}")


    # save config if changed, or --save given
    if args.keys or args.save:
        with open(CONFIG_FILE, "wt") as fp:
            fp.write(f"## Stimela {stimela.__version__} configuration file\n")
            fp.write(f"## Saved on {datetime.now().ctime()}\n\n")
            OmegaConf.save(config=conf.opts, f=fp)
        log.info(f"wrote configuration to {CONFIG_FILE}")
                