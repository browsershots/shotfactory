from distutils.core import setup
import sys

kwargs = {
    'name': 'ShotFactory',
    'version': '0.3-alpha2',
    'description': 'Screenshot factory for browsershots.org',
    'author': 'Johann C. Rocholl',
    'author_email': 'johann@browsershots.org',
    'url': 'http://v03.browsershots.org/',
    'packages': [
        'shotfactory03',
        'shotfactory03.gui',
        'shotfactory03.gui.darwin',
        'shotfactory03.gui.linux',
        'shotfactory03.gui.windows',
        'shotfactory03.image',
        ],
    'scripts': [
        'shotfactory.py',
        'browsershot.py',
        'ppmoffset.py',
        ],
    }

if 'py2exe' in sys.argv:
    import py2exe
    # modulefinder can't handle runtime changes to __path__,
    # but win32com uses them
    import modulefinder
    import win32com
    for path in win32com.__path__[1:]:
        modulefinder.AddPackagePath("win32com", path)
    __import__("win32com.shell")
    m = sys.modules["win32com.shell"]
    for path in m.__path__[1:]:
        modulefinder.AddPackagePath("win32com.shell", path)
    # py2exe configuration
    kwargs['console'] = [{
        'script': 'shotfactory.py',
        'icon_resources': [(1, 'favicon.ico')],
        }]
    kwargs['options'] = {
        'py2exe': {
            'includes': ','.join([
                'shotfactory03.gui.windows.msie',
                'shotfactory03.gui.windows.firefox',
                ]),
            'dist_dir': 'bin',
            }
        }

setup(**kwargs)
