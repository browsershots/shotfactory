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
GUI-specific functions for Firefox on Mac OS X.
"""

__revision__ = '$Rev: 503 $'
__date__ = '$Date: 2006-06-17 08:14:59 +0200 (Sat, 17 Jun 2006) $'
__author__ = '$Author: johann $'

import os, time, appscript, MacOS, shutil
from shotfactory03.gui import darwin as base

class Gui(base.Gui):
    """
    Special functions for Firefox on Mac OS X.
    """

    def reset_browser(self):
        """
        Delete crash dialog and browser cache.
        """
        home = os.environ['HOME'].rstrip('/')
        # Delete cache
        profiles = os.path.join(home,
            'Library', 'Caches', 'Firefox', 'Profiles')
        for profile in os.listdir(profiles):
            cachedir = os.path.join(profiles, profile, 'Cache')
            if os.path.exists(cachedir):
                print 'deleting cache', cachedir
                shutil.rmtree(cachedir)
        # Delete crash dialog
        profiles = os.path.join(home,
            'Library', 'Application Support', 'Firefox', 'Profiles')
        for profile in os.listdir(profiles):
            crashfile = os.path.join(profiles, profile, 'sessionstore.js')
            if os.path.exists(crashfile):
                print 'deleting crash file', crashfile
                os.unlink(crashfile)

    def start_browser(self, config, url, options):
        """
        Start browser and load website.
        """
        self.shell('/Applications/Firefox.app/Contents/MacOS/firefox "%s" &'
                   % url)
        time.sleep(5)
        try:
            self.sysevents = appscript.app('System Events')
        except MacOS.Error, error:
            code, message = error
            raise RuntimeError(message)
        self.firefox_bin = self.sysevents.processes['firefox-bin']
        print "maximizing window"
        self.firefox_bin.frontmost.set(True)
        self.window = self.firefox_bin.windows[1]
        self.window.position.set((0, 22))
        self.window.size.set((self.width, self.height - 26))
        time.sleep(options.wait)
        return True

    def down(self):
        """Scroll down one line."""
        self.sysevents.key_code(125)

    def close(self):
        """Close browser and helper programs."""
        self.shell('killall firefox-bin')
        self.shell('killall UserNotificationCenter')
