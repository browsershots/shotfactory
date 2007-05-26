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

>>> ini_find_section(TEST_LINES, 'User Prefs')
"""

__revision__ = '$Rev$'
__date__ = '$Date$'
__author__ = '$Author$'


import os
import time
from shotfactory03.gui import linux as base


class Gui(base.Gui):
    """
    Special functions for Opera.
    """

    def reset_browser(self):
        """
        Remove evidence of previous browser crash.
        """
        home = os.environ['HOME'].rstrip('/')
        inifile = home + '/.opera/opera6.ini'
        if os.path.exists(inifile):
            print 'removing crash dialog from', inifile
            lines = file(inifile).readlines()
            ini_set(lines, 'User Prefs', 'Run', 0)
            ini_set(lines, 'User Prefs', 'Show New Opera Dialog', 1)
            open(inifile, 'w').write(''.join(lines))

def ini_set(lines, section, key, value):
    if lines[0][-2] == chr(13):
        crlf = lines[0][-2:]
    else:
        crlf = lines[0][-1]
    start, stop = self.ini_find_section(lines, section)
    if start is None:
        lines.append(crlf)
        lines.append('[' + section + ']')
        lines.append(key + '=' + str(value) + crlf)
    else:
        index = self.ini_find_key_line(lines, start, stop, key)
        if index:
            lines[index] = key + '=' + str(value) + crlf
        else:
            lines.insert(stop, key + '=' + str(value) + crlf)


def ini_find_section(lines, section):
    start = None
    for index, line in enumerate(lines):
        if line.startswith('[' + section + ']'):
            start = index
        if start and line.strip() == '':
            return start, index
    if start:
        return start, len(lines)
    return None, None


def ini_find_key_line(lines, start, stop, key):
    for index in range(start, stop):
        if lines[index].startswith(key + '='):
            return index


if __name__ == '__main__':
    import doctest
    TEST_LINES = [
        "[User Prefs]",
        ]
    doctest.testmod()
