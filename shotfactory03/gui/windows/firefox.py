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
GUI-specific interface functions for Mozilla Firefox on Microsoft Windows.
"""

__revision__ = "$Rev$"
__date__ = "$Date$"
__author__ = "$Author$"

import os
import time
import sys
import shutil
import win32api
import win32gui
import win32con
import pywintypes
from win32com.shell import shellcon
from win32com.shell import shell
from shotfactory03.gui import windows


class Gui(windows.Gui):
    """
    Special functions for Firefox on Windows.
    """

    def reset_browser(self, verbose=True):
        """
        Delete previous session and browser cache.
        """
        # Delete old session
        appdata = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)
        profiles = os.path.join(appdata, 'Mozilla', 'Firefox', 'Profiles')
        for profile in os.listdir(profiles):
            session = os.path.join(profiles, profile, 'sessionstore.js')
            if os.path.exists(session):
                if verbose:
                    print "deleting previous session:", session
                os.unlink(session)
        # Delete all files from the browser cache
        appdata = shell.SHGetFolderPath(0, shellcon.CSIDL_LOCAL_APPDATA, 0, 0)
        profiles = os.path.join(appdata, 'Mozilla', 'Firefox', 'Profiles')
        for profile in os.listdir(profiles):
            cache = os.path.join(profiles, profile, 'Cache')
            if os.path.exists(cache):
                if verbose:
                    print "deleting browser cache:", cache
                shutil.rmtree(cache)

    def start_browser(self, config, url, options):
        """
        Start browser and load website.
        """
        if config['command'] == 'firefox':
            command = r'c:\progra~1\mozill~1\firefox.exe'
        else:
            command = config['command']
        print 'running', command
        os.spawnl(os.P_DETACH, command, os.path.basename(command), url)
        print "Sleeping %d seconds while page is loading." % options.wait
        time.sleep(options.wait)

    def down(self, verbose=False):
        """
        Scroll down one line.
        """
        firefox = self.find_window_by_title_suffix(' Firefox', verbose)
        scrollable = self.get_child_window(firefox, verbose)
        self.send_keypress(scrollable, win32con.VK_DOWN)
        time.sleep(0.1)


# Test scrolling from command line
if __name__ == '__main__':
    config = {'width': 1024, 'bpp': 24}
    options = None
    gui = Gui(config, options)
    gui.down(verbose=True)
