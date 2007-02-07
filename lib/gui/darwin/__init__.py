# browsershots.org
# Copyright (C) 2006 Johann C. Rocholl <johann@browsershots.org>
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
GUI-specific interface functions for Mac OS X.
"""

__revision__ = '$Rev: 503 $'
__date__ = '$Date: 2006-06-17 08:14:59 +0200 (Sat, 17 Jun 2006) $'
__author__ = '$Author: johann $'

import os, time, appscript, MacOS
from shotfactory03 import gui as base

class Gui(base.Gui):
    """
    Special functions for Mac OS X.
    """

    def prepare_screen(self):
        self.bottom_skip = 4
        self.safari = None
        # Set screen resolution and color depth with Lynn Pye's cscreen
        # Freeware, available from http://www.pyehouse.com/lynn/cscreen.php
        self.shell('./cscreen -x %d -y %d -d %d -f'
                   % (self.width, self.height, self.bpp))

    def screenshot(self, filename):
        """Save the full screen to a PPM file."""
        self.shell('screencapture "%s.png"' % filename)
        self.shell('pngtopnm "%s.png" > "%s"' % (filename, filename))
