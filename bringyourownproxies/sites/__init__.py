# -*- coding: utf-8 -*-
#!/usr/bin/python
#!/usr/bin/python
import os
import sys

cwd = os.path.dirname(os.path.realpath(__file__))
files = os.listdir(cwd)
modules = [f for f in files if not f.endswith('.py') and not f.endswith('.pyc')]
allm = []
for d in modules:
    cur = os.path.join(cwd,d)
    if os.path.isdir(cur):

        for f in os.listdir(cur):
            if os.path.isfile(os.path.join(cur,f)):
                if f != '__init__.py' and f.endswith('.py'):
                    allm.append("from {sites}.{d}.{f} import *".format(sites='bringyourownproxies.sites',d=d,f=f[:-3]))

for m in allm:
    exec(m)
