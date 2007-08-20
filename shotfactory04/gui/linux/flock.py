# browsershots.org - Test your web design in different browsers
# Copyright (C) 2007 Johann C. Rocholl <johann@browsershots.org>
#
# Browsershots is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Browsershots is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
GUI-specific interface functions for X11.
"""

__revision__ = "$Rev$"
__date__ = "$Date$"
__author__ = "$Author$"


import os
import time
import shutil
from shotfactory04.gui import linux as base


class Gui(base.Gui):
   """
   Special functions for Flock.
   """

   def reset_browser(self):
       """
       Delete crash dialog and browser cache.
       """
       home = os.environ['HOME'].rstrip('/')
       dotdir = os.path.join(home, '.flock/browser')
       if not os.path.exists(dotdir):
            return
       for profile in os.listdir(dotdir):
            # Delete cache
            cachedir = os.path.join(dotdir, profile, 'Cache')
            if os.path.exists(cachedir):
                print 'deleting cache', cachedir
                shutil.rmtree(cachedir)
            # Delete crash dialog
            crashfile = os.path.join(dotdir, profile, 'sessionstore.js')
            if os.path.exists(crashfile):
                print 'deleting crash file', crashfile
                os.unlink(crashfile)
