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
GUI-specific interface functions for Safari on Microsoft Windows.
"""

__revision__ = "$Rev$"
__date__ = "$Date$"
__author__ = "$Author$"

import os
import time
import win32gui
import win32con
from win32com.shell import shellcon
from win32com.shell import shell
from shotfactory04.gui import windows


class Gui(windows.Gui):
    """
    Special functions for Safari on Windows.
    """

    def reset_browser(self, verbose=True):
        """
        Delete browser cache.
        """
        appdata = shell.SHGetFolderPath(0, shellcon.CSIDL_LOCAL_APPDATA, 0, 0)
        self.delete_if_exists(
            os.path.join(appdata, 'Apple Computer', 'Safari', 'Cache.db'),
            message="deleting browser cache:", verbose=verbose)
        self.delete_if_exists(
            os.path.join(appdata, 'Apple Computer', 'Safari', 'icon.db'),
            message="deleting icon cache:", verbose=verbose)

    def start_browser(self, config, url, options):
        """
        Start browser and load website.
        """
        command = config['command'] or r'c:\progra~1\safari\safari.exe'
        print 'running', command
        os.spawnl(os.P_DETACH, command, os.path.basename(command), '-url', url)
        print "Sleeping %d seconds while page is loading." % options.wait
        time.sleep(options.wait)

    def find_scrollable(self, verbose=False):
        """
        Find the scrollable window.
        """
        hwnd = win32gui.WindowFromPoint((self.width/2, self.height/2))
        for parent_level in range(20):
            if not hwnd:
                return None
            if verbose:
                print 'handle', hwnd
                print 'classname', win32gui.GetClassName(hwnd)
                print 'text', win32gui.GetWindowText(hwnd)
                print
            if win32gui.GetClassName(hwnd) == 'WebViewWindowClass':
                return hwnd
            hwnd = win32gui.GetParent(hwnd)

    def down(self, verbose=False):
        """
        Scroll down one line.
        """
        scrollable = self.find_scrollable(verbose)
        if not scrollable:
            return
        win32gui.PostMessage(scrollable, win32con.WM_KEYDOWN, win32con.VK_DOWN)
        win32gui.PostMessage(scrollable, win32con.WM_KEYUP, win32con.VK_DOWN)
        time.sleep(0.1)


# Test scrolling from command line
if __name__ == '__main__':
    config = {'width': 1024, 'bpp': 24}
    options = None
    gui = Gui(config, options)
    gui.down(verbose=True)
