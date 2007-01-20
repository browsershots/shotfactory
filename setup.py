from distutils.core import setup
import sys

kwargs = {
    'name': 'ShotFactory',
    'version': '0.3-alpha2',
    'description': 'Screenshot factory for browsershots.org',
    'author': 'Johann C. Rocholl',
    'author_email': 'johann@browsershots.org',
    'url': 'http://v03.browsershots.org/',
    'package_dir': {'shotfactory03': 'lib', '': 'pypng'},
    'packages': [
        'shotfactory03',
        'shotfactory03.gui',
        'shotfactory03.gui.darwin',
        'shotfactory03.gui.linux',
        'shotfactory03.gui.windows',
        'shotfactory03.image',
        ],
    'scripts': [
        'scripts/ppmoffset',
        'scripts/shotfactory',
        'scripts/browsershot',
        ],
    }

if 'py2exe' in sys.argv:
    import py2exe
    kwargs['console'] = [{
        'script': 'scripts/shotfactory',
        'icon_resources': [(1, 'favicon.ico')],
        }]
    kwargs['options'] = {
        'py2exe': {
            'includes': 'shotfactory03.gui.windows',
            'dist_dir': 'bin',
            }
        }

setup(**kwargs)
