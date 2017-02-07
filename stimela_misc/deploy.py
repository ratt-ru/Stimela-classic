### Don't run this unless you preparing a new release
import sys
import os
import yaml
import json
import codecs
from collections import OrderedDict

version = sys.argv[1]
root = sys.argv[2]

with open('{}/stimela_misc/version.py'.format(root), 'w') as std:
    std.write('version = \'{}\''.format(version))
    

CABS = {}
for cab in os.listdir('{}/stimela/cargo/cab'.format(root)):
    path = '{0}/stimela/cargo/cab/{1}'.format(root, cab)
    if os.path.exists('{}/parameters.json'.format(path)) \
        and os.path.exists('{}/Dockerfile'.format(path)):

        with open('{}/parameters.json'.format(path)) as _std:
            params = yaml.safe_load(_std)

        with open('{}/Dockerfile'.format(path)) as std:
            lines = std.readlines()
            changed = False
            for i,line in enumerate(lines):
                if line.startswith('FROM'):
                    new = 'FROM {0}:{1}\n'.format(params['base'], version)
                    lines[i] = new
                    changed = True

        with open('{}/Dockerfile'.format(path), 'w') as std:
            std.write( ''.join(lines))

        with codecs.open('{}/parameters.json'.format(path), 'w', 'utf8') as std:

            _params = OrderedDict([('task', params['task']),
                                  ('base', params['base']),
                                  ('tag', version),
                                  ('description', params['description']),
                                  ('prefix', params['prefix']),
                                  ('binary', params['binary']),
                                  ('msdir', params['msdir']),
                                  ('parameters', params['parameters'])])

            std.write(json.dumps(_params, indent=4, ensure_ascii=False))


for base in os.listdir('{0}/stimela/cargo/base'.format(root)):
    path = '{0}/stimela/cargo/base/{1}'.format(root, base)
    if not os.path.exists('{}/Dockerfile'.format(path)):
        continue

    with open('{}/Dockerfile'.format(path)) as std:
        lines = std.readlines()
        changed = False

        for i,line in enumerate(lines):
            if line.startswith('FROM') and line.split()[1].startswith('stimela'):
                image = line.split()[1].split(':')[0]
                new = 'FROM {0}:{1}\n'.format(image, version)
                print new
                lines[i] = new
                changed = True

    if changed:
        with open('{}/Dockerfile'.format(path), 'w') as std:
            std.write(''.join(lines))
