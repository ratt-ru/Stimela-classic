import os
import sys
import json
import yaml
import time
import subprocess
from io import StringIO
import codecs
from datetime import datetime
import logging


class StimelaLogger(object):
    def __init__(self, lfile, jtype="docker"):

        self.lfile = lfile
        # Create file if it does not exist
        if not os.path.exists(self.lfile):
            with open(lfile, 'w') as wstd:
                wstd.write('{}')

        self.info = self.read(lfile)
        # First make sure that all fields are
        # initialised. Initialise if not so
        changed = False
        for item in ['images', 'containers', 'processes']:
            if self.info.get(item, None) is None:
                self.info[item] = {}
                changed = True
        if changed:
            self.write()

        self.jtype = jtype

    def _inspect(self, name):

        output = subprocess.check_output(
            "{0:s} inspect {1:s}".format(self.jtype, name), shell=True).decode()
        if self.jtype in ["docker", "podman"]:
            output_file = StringIO(output[3:-3])
        else:
            output_file = StringIO(output)
        jdict = yaml.safe_load(output_file)
        output_file.close()

        return jdict

    def log_image(self, name, image_dir, replace=True, cab=False):
        info = self._inspect(name)
        if self.jtype in ["docker", "podman"]:
            if name not in self.info['images'].keys() or replace:
                self.info['images'][name] = {
                    'TIME':   info['Created'].split('.')[0].replace('Z', '0'),
                    'ID':   info['Id'].split(':')[-1],
                    'CAB':   cab,
                    'DIR':   image_dir,
                }
            else:
                print('Image {0} has already been logged.'.format(name))
        else:
            if name not in self.info['images'].keys() or replace:
                self.info['images'][name] = {
                    'TIME':   info['created'].split('.')[0].replace('Z', '0'),
                    'ID':   info['id'],
                    'CAB':   cab,
                    'DIR':   image_dir,
                }
            else:
                print('Image {0} has already been logged.'.format(name))

    def log_container(self, name):
        info = self._inspect(name)

        if self.jtype in ["docker", "podman"]:
            if name not in self.info['containers'].keys():
                self.info['containers'][name] = {
                    'TIME':   info['Created'].split('.')[0].replace('Z', '0'),
                    'IMAGE':   info['Config']['Image'],
                    'ID':   info['Id'],
                }
            else:
                print('contaier {0} has already been logged.'.format(name))
        else:
            if name not in self.info['containers'].keys():
                self.info['containers'][name] = {
                    'TIME':   info['created'].split('.')[0].replace('Z', '0'),
                    'IMAGE':   info['config']['Image'],
                    'ID':   info['id'],
                }
            else:
                print('contaier {0} has already been logged.'.format(name))

    def log_process(self, pid, name):
        pid = str(pid)
        timestamp = time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime())
        if pid not in self.info['processes'].keys():
            self.info['processes'][pid] = {
                'NAME':   name,
                'TIME':   timestamp,
            }
        else:
            print('PID {0} has already been logged.'.format(pid))

    def remove(self, ltype, name):
        try:
            self.info[ltype].pop(str(name))
        except:
            print('WARNING:: Could not remove object \'{0}:{1}\' from logger'.format(
                ltype, name))

    def read(self, lfile=None):
        try:
            with open(lfile or self.lfile) as _std:
                jdict = yaml.safe_load(_std)
        except IOError:
            return {}

        return jdict

    def write(self, lfile=None):
        with codecs.open(lfile or self.lfile, 'w', 'utf8') as std:
            std.write(json.dumps(self.info, ensure_ascii=False, indent=4))

    def clear(self, ltype):
        self.info[ltype] = {}

    def display(self, ltype):
        things = sorted(self.info[ltype].items(), key=lambda a: a[1]['TIME'])
        if ltype == 'images':
            print('{0:<36}      {1:<24}     {2:<24}'.format(
                'IMAGE', 'ID', 'CREATED/PULLED'))
            for name, thing in things:
                print('{0:<36}      {1:<24}     {2:<24}'.format(
                    name, thing['ID'][:8], thing['TIME']))

        if ltype == 'containers':
            print('{0:<36}      {1:<24}     {2:<24}     {3:<24}      {4:<24}'.format(
                'CONTAINER', 'CAB IMAGE', 'ID', 'STARTED', 'UPTIME'))
            for name, thing in things:
                started = datetime.strptime(thing['TIME'], '%Y-%m-%dT%H:%M:%S')
                finished = datetime.utcnow()
                mins = (finished - started).total_seconds()/60
                hours, mins = divmod(mins, 60)
                mins, secs = divmod(mins*60, 60)

                uptime = '{0:d}:{1:d}:{2:.2f}'.format(
                    int(hours), int(mins), secs)
                print('{0:<36}      {1:<24}     {2:<24}     {3:<24}      {4:<24}'.format(
                    name, thing['IMAGE'], thing['ID'][:8], thing['TIME'], uptime))

        if ltype == 'processes':
            print('{0:<36}      {1:<24}     {2:<24}     {3:24}'.format(
                'PID', 'NAME', 'STARTED', 'UPTIME'))
            for name, thing in things:
                started = datetime.strptime(thing['TIME'], '%Y-%m-%dT%H:%M:%S')
                finished = datetime.utcnow()
                mins = (finished - started).total_seconds()/60
                hours, mins = divmod(mins, 60)
                mins, secs = divmod(mins*60, 60)

                uptime = '{0:d}:{1:d}:{2:.2f}'.format(
                    int(hours), int(mins), secs)
                print('{0:<36}      {1:<24}     {2:<24}     {3:24}'.format(
                    name, thing['NAME'], thing['TIME'], uptime))


class MultiplexingHandler(logging.Handler):
    """handler to send INFO and below to stdout, everything above to stderr"""
    def __init__(self, info_stream=sys.stdout, err_stream=sys.stderr):
        super(MultiplexingHandler, self).__init__()
        self.info_handler = logging.StreamHandler(info_stream)
        self.err_handler = logging.StreamHandler(err_stream)
        self.multiplex = True

    def emit(self, record):
        handler = self.err_handler if record.levelno > logging.INFO and self.multiplex else self.info_handler
        handler.emit(record)
        # ignore broken pipes, this often happens when cleaning up and exiting
        try:
            handler.flush()
        except BrokenPipeError:
            pass

    def flush(self):
        try:
            self.err_handler.flush()
            self.info_handler.flush()
        except BrokenPipeError:
            pass

    def close(self):
        self.err_handler.close()
        self.info_handler.close()

    def setFormatter(self, fmt):
        self.err_handler.setFormatter(fmt)
        self.info_handler.setFormatter(fmt)

class ConsoleColors():
    WARNING = '\033[93m' if sys.stdin.isatty() else ''
    ERROR   = '\033[91m' if sys.stdin.isatty() else ''
    BOLD    = '\033[1m'  if sys.stdin.isatty() else ''
    DIM     = '\033[2m'  if sys.stdin.isatty() else ''
    GREEN   = '\033[92m' if sys.stdin.isatty() else ''
    ENDC    = '\033[0m'  if sys.stdin.isatty() else ''

    BEGIN = "<COLORIZE>"
    END   = "</COLORIZE>"

    @staticmethod
    def colorize(msg, *styles):
        style = "".join(styles)
        return msg.replace(ConsoleColors.BEGIN, style).replace(ConsoleColors.END, ConsoleColors.ENDC if style else "")

class ColorizingFormatter(logging.Formatter):
    """This Formatter inserts color codes into the string according to severity"""
    def __init__(self, fmt=None, datefmt=None, style="%", default_color=None):
        super(ColorizingFormatter, self).__init__(fmt, datefmt, style)
        self._default_color = default_color or ""

    def format(self, record):
        style = ConsoleColors.BOLD if hasattr(record, 'boldface') else ""
        if hasattr(record, 'color'):
            style += getattr(ConsoleColors, record.color or "None", "")
        elif record.levelno >= logging.ERROR:
            style += ConsoleColors.ERROR
        elif record.levelno >= logging.WARNING:
            style += ConsoleColors.WARNING
        return ConsoleColors.colorize(super(ColorizingFormatter, self).format(record), style or self._default_color)


class SelectiveFormatter(logging.Formatter):
    """Selective formatter. if condition(record) is True, invokes other formatter"""
    def __init__(self, default_formatter, dispatch_list):
        self._dispatch_list = dispatch_list
        self._default_formatter = default_formatter

    def format(self, record):
        for condition, formatter in self._dispatch_list:
            if condition(record):
                return formatter.format(record)
        else:
            return self._default_formatter.format(record)


