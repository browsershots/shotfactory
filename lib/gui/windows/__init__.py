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

import os, time, sys
import win32api, win32gui, win32con, pywintypes
from shotfactory03 import gui as base

class Gui(base.Gui):
    """
    Special functions for Windows.
    """

    def __init__(self, width, height, bpp, dpi):
        base.Gui.__init__(self, width, height, bpp, dpi)
        # Set screen resolution with Stefan Tucker's Resolution Changer
        # Freeware, available from http://www.12noon.com/reschange.htm
        self.shell('reschangecon.exe -width=%u -height=%u -depth=%u > NUL'
                   % (width, height, bpp))

    def shell(self, command):
        """Run a shell command."""
        return os.system(command)

    def hide_mouse(self):
        """Move the mouse cursor out of the way."""
        win32api.SetCursorPos((0, 0))

    def screenshot(self, filename):
        """Save the full screen to a PPM file."""
        import ImageGrab
        import PpmImagePlugin
        im = ImageGrab.grab()
        outfile = open(filename, 'wb')
        im.save(outfile, 'PPM')
        outfile.close()

    def down(self):
        """Scroll down one line."""
        try:
            if self.scroll_window:
                win32gui.PostMessage(self.scroll_window,
                                     win32con.WM_VSCROLL,
                                     win32con.SB_LINEDOWN, 0)
        except pywintypes.error:
            pass
        time.sleep(0.1)

    def start_browser(self, config, url, options):
        """Start browser and load website."""
        self.close()
        if config['command'] == 'msie':
            command = r'c:\progra~1\intern~1\iexplore.exe'
        else:
            command = config['command']
        print 'running', command
        os.spawnl(os.P_DETACH, command, os.path.basename(command), url)
        print "Sleeping %d seconds while page is loading." % options.wait
        time.sleep(options.wait)

    def close(self):
        """Close the browser."""
        # win32gui.PostMessage(self.msie_window, win32con.WM_CLOSE, 0, 0)
        process_names = (
            'iexplore.exe',
            'firefox.exe',
            'dwwin.exe',
            'iedw.exe',
            'telnet.exe',
            'msimn.exe',
            )
        for name in process_names:
            # Kill all processes matching name, using
            # pv.exe from teamcti.com (freeware):
            # http://www.teamcti.com/pview/prcview.htm
            os.system('pv.exe -kf %s "2>nul" > nul' % name)

    def find_window_by_title_suffix(self, suffix, verbose=False):
        """Find a window on the desktop where the title ends as specified."""
        try:
            desktop = win32gui.GetDesktopWindow()
            if verbose:
                print "GetDesktopWindow() => %d" % desktop
            window = win32gui.GetWindow(desktop, win32con.GW_CHILD)
            if verbose:
                print "GetWindow(%d, GW_CHILD) => %d" % (desktop, window)
            while True:
                title = win32gui.GetWindowText(window)
                if verbose:
                    print "GetWindowText(%d) => '%s'" % (window, title)
                if title.endswith(suffix):
                    break
                previous = window
                window = win32gui.GetWindow(previous, win32con.GW_HWNDNEXT)
                if verbose:
                    print "GetWindow(%d, GW_HWNDNEXT) => %d" % (previous, window)
        except pywintypes.error:
            window = 0
        return window

    def get_child_window(self, parent, verbose=False):
        try:
            window = win32gui.GetWindow(parent, win32con.GW_CHILD)
        except pywintypes.error:
            window = 0
        if verbose:
            print "GetWindow(%d, GW_CHILD) => %d" % (parent, window)
        return window

    def find_window_by_classname(self, classname, verbose=False):
        """Wrapper for win32gui.FindWindow."""
        try:
            window = win32gui.FindWindow(classname, None)
        except pywintypes.error:
            window = 0
        if verbose:
            print "FindWindow('%s', None) => %d" % (classname, window)
        return window

    def find_child_window_by_classname(self, parent, classname, verbose=False):
        """Wrapper for win32gui.FindWindowEx."""
        try:
            window = win32gui.FindWindowEx(parent, 0, classname, None)
        except pywintypes.error:
            window = 0
        if verbose:
            print "FindWindowEx(%d, 0, '%s', None) => %d" % (
                parent, classname, window)
        return window

    def send_keypress(self, window, key):
        """Post key down and up events to the specified window."""
        win32gui.PostMessage(window, win32con.WM_KEYDOWN, key)
        win32gui.PostMessage(window, win32con.WM_KEYUP, key)
