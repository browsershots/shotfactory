# browsershots.org ShotFactory 0.3-beta1
# Copyright (C) 2007 Johann C. Rocholl <johann@browsershots.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston,
# MA 02111-1307, USA.

"""
GUI-specific interface functions for X11.
"""

__revision__ = "$Rev$"
__date__ = "$Date$"
__author__ = "$Author$"

import os
import time
from shotfactory03.gui import linux as base


class Gui(base.Gui):
    """
    Special functions for Galeon.
    """

    def reset_browser(self):
        """
        Delete evidence of previous browser crash.
        """
        home = os.environ['HOME'].rstrip('/')
        crashfile = home + '/.galeon/session_crashed.xml'
        if os.path.exists(crashfile):
            print 'deleting crash file', crashfile
            os.unlink(crashfile)
