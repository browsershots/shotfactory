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
import win32api, win32gui, win32con
from shotfactory03.gui.base import BaseGui

class WindowsGui(BaseGui):
    """
    Special functions for Windows.
    """

    def __init__(self, width, height, bpp, dpi):
        BaseGui.__init__(self, width, height, bpp, dpi)
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
        im = ImageGrab.grab()
        outfile = open(filename, 'wb')
        im.save(outfile, 'PPM')
        outfile.close()

    def down(self):
        """Scroll down one line."""
        if self.scroll_window:
            win32gui.PostMessage(self.scroll_window,
                                 win32con.WM_VSCROLL,
                                 win32con.SB_LINEDOWN, 0)
        time.sleep(0.1)

    def start_browser(self, browser, url):
        """Start browser and load website."""
        self.close()
        command = 'c:\progra~1\intern~1\iexplore.exe'
        os.spawnl(os.P_DETACH, command, 'iexplore', url)
        self.msie_window = 0
        self.scroll_window = 0
        timeout = 20
        while timeout > 0:
            try:
                self.msie_window = window_by_classname('IEFrame')
                self.scroll_window = child_window_by_classname(
                    self.msie_window, 'Internet Explorer_Server')
                break
            except KeyError:
                pass
            print "MSIE is not ready (timeout in %d seconds)." % timeout
            time.sleep(5)
            timeout -= 5
        print "Sleeping 20 seconds while page is loading."
        time.sleep(20)

    def close(self):
        """Close the browser."""
        # Using process.exe from beyondlogic.org (freeware):
        # http://www.beyondlogic.org/solutions/processutil/processutil.htm
        # win32gui.PostMessage(self.msie_window, win32con.WM_CLOSE, 0, 0)
        os.system("process.exe -k iexplore.exe > NUL")

        # Kill crash report system
        os.system("process.exe -k dwwin.exe > NUL")
        os.system("process.exe -k iedw.exe > NUL")
        os.system("process.exe -k telnet.exe > NUL")
        # Kill image preview
        os.system("process.exe -k rundll32.exe > NUL")
        # Kill Outlook Express internet connection wizard
        os.system("process.exe -k msimn.exe > NUL")
        # It would be better to close all open windows except own console,
        # or maybe kill all processes except those which ran at start.


def enum_classname_hwnd(hwnd, extra):
    extra[win32gui.GetClassName(hwnd)] = hwnd


def window_by_classname(classname):
    extra = {}
    win32gui.EnumWindows(enum_classname_hwnd, extra)
    return extra[classname]


def child_window_by_classname(hwnd, classname):
    extra = {}
    win32gui.EnumChildWindows(hwnd, enum_classname_hwnd, extra)
    return extra[classname]


def enum_print(hwnd, extra):
    print hwnd, win32gui.GetClassName(hwnd)


def print_child_windows(hwnd):
    win32gui.EnumChildWindows(hwnd, enum_print, 0)
