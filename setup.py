from distutils.core import setup

setup(name = 'ShotFactory',
      version = '0.3-alpha1',
      description = 'Screenshot factory for browsershots.org',
      author = 'Johann C. Rocholl',
      author_email = 'johann@browsershots.org',
      url = 'http://v03.browsershots.org/',
      package_dir = {'shotfactory03': 'lib', '': 'pypng'},
      packages = [
            'shotfactory03',
            'shotfactory03.gui',
            'shotfactory03.image',
            'shotfactory03.pypng',
            ],
      scripts = [
            'scripts/ppmoffset',
            'scripts/shotfactory',
            'scripts/browsershot',
            ],
      )
