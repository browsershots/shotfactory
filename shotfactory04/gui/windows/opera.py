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
GUI-specific interface functions for Opera on Microsoft Windows.
"""

__revision__ = "$Rev: 1850 $"
__date__ = "$Date: 2007-07-12 17:53:13 +0100 (Do, 12 Jul 2007) $"
__author__ = "$Author: johann $"

import os
import time
import sys
import win32api
import win32gui
import win32con
import pywintypes
from win32com.shell import shellcon
from win32com.shell import shell
from shotfactory04.gui import windows
from shotfactory04.inifile import IniFile


class Gui(windows.Gui):
    """
    Special functions for Safari on Windows.
    """

    def reset_browser(self, verbose=True):
        """
        Disable crash dialog and delete browser cache.
        """
        appdata = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)
        profile = os.path.join(appdata, 'Opera', 'Opera', 'profile')
        # Disable crash dialog
        inifile = os.path.join(profile, 'opera6.ini')
        if os.path.exists(inifile):
            print 'removing crash dialog from', inifile
            ini = IniFile(inifile)
            ini.set('State', 'Run', 0)
            ini.set('User Prefs', 'Show New Opera Dialog', 0)
            ini.save()
        # Delete all files from the browser cache
        self.delete_if_exists(
            os.path.join(profile, 'cache4'),
            message="deleting browser cache:", verbose=verbose)        

    def start_browser(self, config, url, options):
        """
        Start browser and load website.
        """
        command = config['command'] or r'c:\progra~1\opera\opera.exe'
        print 'running', command
        os.spawnl(os.P_DETACH, command, os.path.basename(command), '-url', url)
        print "Sleeping %d seconds while page is loading." % options.wait
        time.sleep(options.wait)

    def find_scrollable(self, verbose=False):
        """
        Find the scrollable window.
        """
        hWnd = win32gui.WindowFromPoint((self.width/2, self.height/2))
        for parent_level in range(20):
            if not hWnd:
                return None
            if verbose:
                print 'handle', hWnd
                print 'classname', win32gui.GetClassName(hWnd)
                print 'text', win32gui.GetWindowText(hWnd)
                print
            if win32gui.GetClassName(hWnd) == 'OperaWindowClass':
                return hWnd
            hWnd = win32gui.GetParent(hWnd)

    def down(self, verbose=False):
        """
        Scroll down one line.
        """
        scrollable = self.find_scrollable(verbose)
        if not scrollable:
            return
        self.send_keypress(scrollable, win32con.VK_DOWN)
        time.sleep(0.1)

# Test scrolling from command line
if __name__ == '__main__':
    config = {'width': 1024, 'bpp': 24}
    options = None
    gui = Gui(config, options)
    time.sleep(2) # Press Alt+Tab now!
    gui.down(verbose=True)
