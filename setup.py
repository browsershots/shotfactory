# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name = 'ShotFactory',
      version = '0.3.0',
      description = 'Server software for browsershots.org',
      author = 'Johann C. Rocholl',
      author_email = 'johann@browsershots.org',
      url = 'http://browsershots.org/',
      package_dir = {'shotfactory03': 'lib', '': 'pypng'},
      packages = [
            'shotfactory03',
            'shotfactory03.gui',
            'shotfactory03.image',
            ],
      py_modules = ['png'],
      scripts = [
            'scripts/ppmoffset',
            'scripts/shotfactory',
            'scripts/browsershot',
            ],
      )
