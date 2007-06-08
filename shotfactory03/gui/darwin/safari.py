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
GUI-specific functions for Safari on Mac OS X.
"""

__revision__ = "$Rev$"
__date__ = "$Date$"
__author__ = "$Author$"

import os
import time
import appscript
import MacOS
from shotfactory03.gui import darwin as base


class Gui(base.Gui):
    """
    Special functions for Safari on Mac OS X.
    """

    def js(self, command):
        """Run JavaScript in Safari."""
        try:
            return self.safari.do_JavaScript(
                command, in_=self.safari.documents[0])
        except:
            return None

    def start_browser(self, config, url, options):
        """
        Start browser and load website.
        """
        try:
            self.safari = appscript.app('Safari')
        except MacOS.Error, error:
            code, message = error
            raise RuntimeError(message)
        self.js("window.moveTo(0,0)")
        time.sleep(0.1)
        self.js("window.resizeTo(screen.availWidth,screen.availHeight)")
        time.sleep(0.1)
	try:
            self.safari.activate()
	except:
	    raise RuntimeError("Could not activate Safari.")
        time.sleep(0.1)
        self.js("document.location='%s'" % url)
        ready_count = 0
        max_wait = time.time() + 60
        min_wait = 20
        while time.time() < max_wait:
            time.sleep(1)
            if self.ready_state():
                ready_count += 1
                print ready_count,
                if ready_count >= min_wait:
                    break
            elif ready_count:
                print 'still loading'
                ready_count = 0
        if ready_count >= min_wait:
            print 'done'
        elif ready_count:
            print 'timeout'
        return True

    def ready_state(self):
        """Get progress indicator."""
        state = self.js("document.readyState")
        # print state
        return state == 'complete'

    def scroll_down(self, pixels):
        """Scroll down with AppleScript/JavaScript."""
        self.js('window.scrollBy(0,%d)' % pixels)

    def close(self):
        """Close Safari."""
        base.Gui.close(self)
        self.shell('killall Safari > /dev/null 2>&1')
