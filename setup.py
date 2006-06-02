# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name = 'ShotFactory',
      version = '0.3.0',
      description = 'Server software for browsershots.org',
      author = 'Johann C. Rocholl',
      author_email = 'johann@browsershots.org',
      url = 'http://browsershots.org/',
      package_dir = {'shotfactory03': 'lib'},
      packages = [
            'shotfactory03',
            ],
      scripts = [
            'scripts/shotfactory03.py',
            'scripts/shotfactory03_formatting.py',
            'scripts/xmlrpc_help.py',
            ],
      )
