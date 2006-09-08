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


import os, time
from shotfactory03.gui.base import BaseGui


class X11Gui(BaseGui):
    """
    Special functions for the X11 screen.
    """

    def __init__(self, width, height, bpp, dpi, display=':1'):
        """
        Start a VNC server.
        """
        BaseGui.__init__(self, width, height, bpp, dpi)
        self.display = display
        command = ('vncserver %s -geometry %dx%d -depth %d -dpi %d'
                   % (display, width, height, bpp, dpi))
        for attempts in range(10):
            error = os.system(command)
            if not error:
                break
            print 'could not start vncserver, trying again in 3 seconds'
            time.sleep(3)
        if error:
            raise RuntimeError('could not start vncserver')

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

    def hide_mouse(self):
        """Move the mouse cursor out of the way."""
        self.shell('xte "mousemove 400 0"')

    def screenshot(self, filename):
        """Save the full screen to a PPM file."""
        parts = ('xwd -root -silent',
                 'xwdtopnm',
                 'pnmdepth 255 > "%s"' % filename)
        error = self.shell('|'.join(parts))
        if error:
            raise RuntimeError('screenshot failed')

    def remove_crash_dialog(self, browser):
        """Delete evidence of browser crash."""
        home = os.environ['HOME'].rstrip('/')
        crashfile = ''
        if browser == 'Opera':
            inifile = home + '/.opera/opera6.ini'
            if os.path.exists(inifile):
                print 'removing crash dialog from', inifile
                os.system("sed -i -e 's/^Run=[0-9]$/Run=0/g' " + inifile)
            else:
                print 'file does not exist:', inifile
        elif browser == 'Galeon':
            crashfile = home + '/.galeon/session_crashed.xml'
        elif browser == 'Epiphany':
            crashfile = home + '/.gnome2/epiphany/session_crashed.xml'
        if crashfile and os.path.exists(crashfile):
            print 'deleting crash file', crashfile
            os.unlink(crashfile)

    def start_browser(self, config, url):
        """Start browser and load website."""
        self.remove_crash_dialog(config['browser'])
        self.shell('%s "%s" &' % (config['command'], url))
        time.sleep(24)
        self.maximize()
        time.sleep(4)

    def close(self):
        """Shut down the VNC server."""
        error = os.system('vncserver -kill %s' % self.display)
        assert not error
        os.system('killall -9 klauncher')
        os.system('killall -9 dcopserver')
        os.system('killall -9 kio_http')
        os.system('killall -9 artsd')
