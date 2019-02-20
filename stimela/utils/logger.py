import os
import sys
import json
import yaml
import time
import subprocess
from cStringIO import StringIO as io
import codecs
from datetime import datetime

class StimelaLogger(object):
    def __init__(self, lfile):

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

    def _inspect(self, name):
        output = subprocess.check_output("docker inspect {}".format(name), shell=True)
        output_file = io(output[3:-3])
        jdict = yaml.safe_load(output_file)
        output_file.close()

        return jdict

    def log_image(self, name, image_dir, replace=False, cab=False):
        info = self._inspect(name)

        if name not in self.info['images'].keys() or replace:
            self.info['images'][name] = {
                'TIME'      :   info['Created'].split('.')[0].replace('Z', '0'),
                'ID'        :   info['Id'].split(':')[1],
                'CAB'       :   cab,
                'DIR'       :   image_dir, 
            }
        else:
            print('Image {0} has already been logged.'.format(name))

    def log_container(self, name):
        info = self._inspect(name)

        if name not in self.info['containers'].keys():
            self.info['containers'][name] = {
                'TIME'      :   info['Created'].split('.')[0].replace('Z', '0'),
                'IMAGE'     :   info['Config']['Image'],
                'ID'        :   info['Id'],
            }
        else:
            print('contaier {0} has already been logged.'.format(name))

    def log_process(self, pid, name):
        pid = str(pid)
        timestamp = time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime())
        if pid not in self.info['processes'].keys():
            self.info['processes'][pid] = {
                'NAME'  :   name,
                'TIME'  :   timestamp,
            }
        else:
            print('PID {0} has already been logged.'.format(pid))


    def remove(self, ltype, name):
        try:
            self.info[ltype].pop(str(name))
        except:
            print('WARNING:: Could not remove object \'{0}:{1}\' from logger'.format(ltype, name))
    
    
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
            print('{0:<36}      {1:<24}     {2:<24}'.format('IMAGE', 'ID', 'CREATED/PULLED'))
            for name, thing in things:
                print('{0:<36}      {1:<24}     {2:<24}'.format(name, thing['ID'][:8], thing['TIME']))

        if ltype == 'containers':
            print('{0:<36}      {1:<24}     {2:<24}     {3:<24}      {4:<24}'.format('CONTAINER','CAB IMAGE', 'ID', 'STARTED', 'UPTIME'))
            for name, thing in things:
                started = datetime.strptime(thing['TIME'], '%Y-%m-%dT%H:%M:%S')
                finished = datetime.utcnow()
                mins = (finished - started).total_seconds()/60
                hours, mins = divmod(mins, 60)
                mins, secs = divmod(mins*60, 60)

                uptime = '{0:d}:{1:d}:{2:.2f}'.format(int(hours), int(mins), secs)
                print('{0:<36}      {1:<24}     {2:<24}     {3:<24}      {4:<24}'.format(name, thing['IMAGE'], thing['ID'][:8], thing['TIME'], uptime))

        if ltype == 'processes':
            print('{0:<36}      {1:<24}     {2:<24}     {3:24}'.format('PID','NAME', 'STARTED', 'UPTIME'))
            for name, thing in things:
                started = datetime.strptime(thing['TIME'], '%Y-%m-%dT%H:%M:%S')
                finished = datetime.utcnow()
                mins = (finished - started).total_seconds()/60
                hours, mins = divmod(mins, 60)
                mins, secs = divmod(mins*60, 60)

                uptime = '{0:d}:{1:d}:{2:.2f}'.format(int(hours), int(mins), secs)
                print('{0:<36}      {1:<24}     {2:<24}     {3:24}'.format(name,thing['NAME'], thing['TIME'], uptime))
