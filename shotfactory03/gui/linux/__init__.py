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
from shotfactory03 import gui as base


class Gui(base.Gui):
    """
    Special functions for the X11 screen.
    """

    def prepare_screen(self):
        """
        Start a VNC server with requested resolution.
        """
        command = ('vncserver %s -geometry %dx%d -depth %d -dpi %d'
                   % (self.display, self.width, self.height,
                      self.bpp, self.dpi))
        attempts = 3
        for attempt in range(attempts):
            error = os.system(command)
            if not error:
                break
            print 'vncserver error (attempt %d out of %d)' % (
                attempt + 1, attempts)
            if attempt + 1 < attempts:
                time.sleep(5)
        if error:
            self.force_quit_vnc_server()
            raise RuntimeError('could not start vncserver')
        # Move the mouse cursor out of the way
        self.shell('xte "mousemove 400 0"')

    def force_quit_vnc_server(self):
        """
        Try to kill old VNC server on my display.
        """
        print "trying to kill old VNC server"
        os.system('vncserver -kill %s' % self.display)
        time.sleep(10)
        os.system('killall -q -9 vncserver')
        host, numeric = self.display.rsplit(':', 1)
        numeric = int(numeric)
        self.delete_if_exists('/tmp/.X%d-lock' % numeric)
        self.delete_if_exists('/tmp/.X11-unix/X%d' % numeric)

    def delete_if_exists(self, filename):
        """Delete file if it exists."""
        if os.path.exists(filename):
            os.unlink(filename)

    def shell(self, command):
        """Run a shell command on my display."""
        return os.system('DISPLAY=%s %s' % (self.display, command))

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

    def screenshot(self, filename):
        """
        Save the full screen to a PPM file.
        """
        parts = ('xwd -root -silent',
                 'xwdtopnm',
                 'pnmdepth 255 > "%s"' % filename)
        error = self.shell('|'.join(parts))
        if error:
            raise RuntimeError('screenshot failed')

    def start_browser(self, config, url, options):
        """
        Start browser and load website.
        """
        self.shell('%s "%s" &' % (config['command'], url))
        print "Sleeping %d seconds while page is loading." % options.wait
        time.sleep(options.wait - 5)
        self.maximize()
        time.sleep(5)

    def close(self):
        """
        Shut down the VNC server.
        """
        error = os.system('vncserver -kill %s' % self.display)
        time.sleep(1)
        os.system('killall -q -9 klauncher')
        os.system('killall -q -9 dcopserver')
        os.system('killall -q -9 kio_http')
        os.system('killall -q -9 artsd')
        os.system('killall -q -9 nspluginviewer')
