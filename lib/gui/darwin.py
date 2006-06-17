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
from array import array
from shotfactory03.gui.base import BaseGui
from shotfactory03.image import hashmatch
from shotfactory03.pypng import png

class DarwinGui(BaseGui):
    """
    Special functions for Mac OS X.
    """

    def __init__(self, width, height, bpp, dpi):
        BaseGui.__init__(self, width, height, bpp, dpi)
        self.bottom_skip = 4
        self.safari = None
        # Set screen resolution and color depth with Lynn Pye's cscreen
        # Freeware, available from http://www.pyehouse.com/lynn/cscreen.php
        self.shell('./cscreen -x %d -y %d -d %d -f' % (width, height, bpp))

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

    def js(self, command):
        """Run JavaScript in Safari."""
        try:
            return self.safari.do_JavaScript(command, in_=self.safari.documents[0])
        except appscript.specifier.CommandError:
            return None

    def start_browser(self, browser, url):
        """Start browser and load website."""
        self.close()

        try:
            self.safari = appscript.app('Safari')
        except MacOS.Error:
            return False

        self.js("window.moveTo(0,0)")
        time.sleep(0.1)
        self.js("window.resizeTo(screen.availWidth,screen.availHeight)")
        time.sleep(0.1)
        self.safari.activate()
        time.sleep(0.1)
        self.js("document.location='%s'" % url)
        ready_count = 0
        max_wait = time.time() + 30
        while time.time() < max_wait:
            time.sleep(1)
            if self.ready_state():
                ready_count += 1
                if ready_count > 5:
                    break
            else:
                ready_count = 0
        return True

    def ready_state(self):
        """Get progress indicator."""
        state = self.js("document.readyState")
        # print state
        return state == 'complete'

    def scroll_down(self, pixels):
        """Scroll down with AppleScript/JavaScript."""
        self.js('window.scrollBy(0,%d)' % pixels)

    def close(self):
        """Close Safari."""
        self.shell('killall Safari')
