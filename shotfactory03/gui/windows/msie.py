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
GUI-specific interface functions for Internet Explorer on Microsoft Windows.
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
import _winreg
from win32com.shell import shellcon
from win32com.shell import shell
from shotfactory03.gui import windows


class Gui(windows.Gui):
    """
    Special functions for MSIE on Windows.
    """

    def reset_browser(self, verbose=False):
        """
        Delete all files from the browser cache.
        """
        cache = shell.SHGetFolderPath(0, shellcon.CSIDL_INTERNET_CACHE, 0, 0)
        cache = os.path.join(cache, 'Content.IE5')
        if not os.path.exists(cache):
            if verbose:
                print "browser cache not found:", cache
            return
        if verbose:
            print "deleting browser cache:", cache
        for filename in os.listdir(cache):
            if filename.lower() == 'index.dat':
                continue
            if verbose:
                print '   ', filename
            try:
                path = os.path.join(cache, filename)
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.unlink(path)
            except (OSError, WindowsError), message:
                print message

    def check_version_override(self, major, minor):
        """
        Raise RuntimeError if conditional comments will be broken.
        """
        root_key = _winreg.HKEY_LOCAL_MACHINE
        key_name = r'Software\Microsoft\Internet Explorer\Version Vector'
        try:
            key = _winreg.OpenKey(root_key, key_name)
            registered = _winreg.QueryValueEx(key, 'IE')[0]
            key.Close()
        except EnvironmentError:
            return
        requested = '%d.%d' % (major, minor)
        while len(requested) < len(registered):
            requested += '0'
        if registered != requested:
            print "This registry key overrides the browser version:"
            print r"HKEY_LOCAL_MACHINE\%s\IE" % key_name
            print "Requested version: %s, Registry override: %s" % (
                requested, registered)
            print "Please rename or delete the key 'IE' with regedit."
            raise RuntimeError("Browser version override in the registry")

    def start_browser(self, config, url, options):
        """
        Start browser and load website.
        """
        self.check_version_override(config['major'], config['minor'])
        if config['command'] == 'msie':
            command = r'c:\progra~1\intern~1\iexplore.exe'
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
        ieframe = self.find_window_by_classname('IEFrame', verbose)
        tabs = self.find_child_window_by_classname(
            ieframe, "TabWindowClass", verbose)
        if tabs:
            ieframe = tabs
        scrollable = self.find_child_window_by_classname(
            ieframe, "Shell DocObject View", verbose)
        self.send_keypress(scrollable, win32con.VK_DOWN)
        time.sleep(0.1)


# Test scrolling from command line
if __name__ == '__main__':
    config = {'width': 1024, 'bpp': 24}
    options = None
    gui = Gui(config, options)
    gui.down(verbose=True)
