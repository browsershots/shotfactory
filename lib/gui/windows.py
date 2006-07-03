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
GUI-specific interface functions for Microsoft Windows.
"""

__revision__ = '$Rev: 503 $'
__date__ = '$Date: 2006-06-17 08:14:59 +0200 (Sat, 17 Jun 2006) $'
__author__ = '$Author: johann $'

import os, time
from array import array
from shotfactory03.gui.base import BaseGui
from shotfactory03.image import hashmatch
from shotfactory03.pypng import png

class WindowsGui(BaseGui):
    """
    Special functions for Windows.
    """

    def __init__(self, width, height, bpp, dpi):
        BaseGui.__init__(self, width, height, bpp, dpi)
        # Set screen resolution and depth with Stefan Tucker's reschange.exe
        # Freeware, available from http://www.12noon.com/reschange.htm
        self.shell('reschange.exe -width=%u -height=%u -depth=%u -refresh=60'
                   % (width, height, bpp))

    def shell(self, command):
        """Run a shell command."""
        return os.system(command)

    def hide_mouse(self):
        """Move the mouse cursor out of the way."""
        pass

    def screenshot(self, filename):
        """Save the full screen to a PPM file."""
        self.shell('screencapture "%s.png"' % filename)
        self.shell('pngtopnm "%s.png" > "%s"' % (filename, filename))

    def scroll_down(self, pixels):
        """Scroll down a number of pixels."""
        self.js('window.scrollBy(0,%d)' % pixels)

    def start_browser(self, browser, url):
        """Start browser and load website."""
        self.close()

        command = 'c:\programme\internet explorer\iexplore.exe'
        os.spawnl(os.P_DETACH, command, 'iexplore', url)
        time.sleep(20)

        return True

    def close(self):
        """Close the browser."""
        pass
