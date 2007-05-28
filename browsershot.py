#!/usr/bin/env python
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
Make screenshots and combine them into one tall image.
"""

__revision__ = "$Rev: 300 $"
__date__ = "$Date: 2006-06-04 23:07:15 +0200 (Sun, 04 Jun 2006) $"
__author__ = "$Author: johann $"

import platform
import optparse
import time


def _main():
    from optparse import OptionParser
    version = '%prog ' + __revision__.strip('$').replace('Rev: ', 'r')
    parser = OptionParser(version=version)
    parser.add_option("-d", dest="display", action="store", type="string",
                      metavar="<name>", default=":0",
                      help="run on a different display (default :0)")
    parser.add_option("-w", dest="wait", action="store", type="int",
                      metavar="<seconds>", default=5,
                      help="wait before taking screenshots (default 5)")
    (options, args) = parser.parse_args()
    config = {'width': 1024, 'bpp': 32}

    system = platform.system()
    if system == 'Linux':
        from shotfactory03.gui import linux
        gui = linux.Gui(config, options)
    else:
        raise NotImplemented(system)

    print "Waiting %d seconds, please activate your browser window..." \
          % options.wait
    time.sleep(options.wait)
    gui.browsershot()

if __name__ == '__main__':
    _main()
