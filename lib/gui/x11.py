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
GUI-specific interface functions for X11.
"""

__revision__ = '$Rev$'
__date__ = '$Date$'
__author__ = '$Author$'


import os
from shotfactory03.gui.base import BaseGui


class X11Gui(BaseGui):
    """
    Special functions for the X11 screen.
    """

    def __init__(self, width, height, bpp, dpi, display=1):
        """
        Start a VNC server.
        """
        command = ('vncserver :%d -geometry %dx%d -depth %d -dpi %d'
                   % (display, width, height, bpp, dpi))
        error = os.system(command)
        assert not error
        self.width = width
        self.height = height
        self.bpp = bpp
        self.dpi = dpi
        self.display = display

    def shell(self, command):
        """Run a shell command on my display."""
        return os.system('DISPLAY=:%d %s' % (self.display, command))

    def home(self):
        """Scroll to the top."""
        self.shell('xte "key Home"')

    def end(self):
        """Scroll to the bottom."""
        self.shell('xte "key End"')

    def pageup(self):
        """Scroll up by one screen page."""
        self.shell('xte "key Page_Up"')

    def pagedown(self):
        """Scroll down by one screen page."""
        self.shell('xte "key Page_Down"')

    def up(self):
        """Scroll up by one line."""
        self.shell('xte "key Up"')

    def down(self):
        """Scroll down by one line."""
        self.shell('xte "key Down"')

    def close_window(self):
        """Close the active window."""
        self.shell('xte "keydown Alt_L"')
        self.shell('xte "key F4"')
        self.shell('xte "keyup Alt_L"')

    def maximize(self):
        """Maximize the active window."""
        self.shell('xte "keydown Alt_L"')
        self.shell('xte "key F10"')
        self.shell('xte "keyup Alt_L"')

    def hide_mouse(self):
        """Move the mouse cursor out of the way."""
        self.shell('xte "mousemove 400 0"')

    def screenshot(self, filename):
        """Save the full screen to a PPM file."""
        self.shell('xwd -root -silent | xwdtopnm | pnmdepth 255 > "%s"' % filename)

    def start_browser(self, browser, url):
        """Start browser and load website."""
        if browser == 'Firefox':
            self.shell('firefox "%s" &' % url)
        elif browser == 'Konqueror':
            self.shell('konqueror "%s" &' % url)
        else:
            raise ValueError("Unsupported browser: %s" % options['browser'])
        time.sleep(24)
        self.maximize()
        time.sleep(4)
