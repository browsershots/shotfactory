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
GUI-specific interface functions for Mac OS X.
"""

__revision__ = "$Rev$"
__date__ = "$Date$"
__author__ = "$Author$"

import os
import time
import appscript
import MacOS
from shotfactory04 import gui as base
from shotfactory04.image import pdf


class Gui(base.Gui):
    """
    Special functions for Mac OS X.
    """

    def shell(self, command):
        """Run a shell command."""
        os.system(command)

    def prepare_screen(self):
        """
        Adjust the screen resolution as requested.
        """
        self.bottom_skip = 4
        self.safari = None
        # Set screen resolution and color depth with Lynn Pye's cscreen
        # Freeware, available from http://www.pyehouse.com/lynn/cscreen.php
        self.shell('./cscreen -x %d -y %d -d %d -f'
                   % (self.width, self.height, self.bpp))

    def screenshot(self, filename):
        """Save the full screen to a PPM file."""
        capture_filename = filename + '.capture'
        self.shell('screencapture "%s"' % capture_filename)
        head = file(capture_filename).read(20)
        if head.startswith('%PDF'): # Mac OS X 10.3 Panther
            width, height, image = pdf.read_pdf(capture_filename)
            pdf.write_ppm(width, height, image, filename)
        else:
            self.shell('pngtopnm "%s" > "%s"' % (capture_filename, filename))
        os.unlink(capture_filename)

    def close(self):
        """Kill helper programs."""
        self.shell('killall UserNotificationCenter > /dev/null 2>&1')
        self.shell('killall "iCal Helper" > /dev/null 2>&1')
