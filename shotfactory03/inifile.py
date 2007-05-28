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
Very simple .ini file manipulator for Opera.

>>> ini = IniFile()
>>> ini.lines = []
>>> ini.set('User Prefs', 'Run', 1)
>>> ini.lines
['[User Prefs]\\n', 'Run=1\\n']
>>> ini.set('User Prefs', 'Show Upgrade Dialog', 0)
>>> ini.lines
['[User Prefs]\\n', 'Run=1\\n', 'Show Upgrade Dialog=0\\n']
>>> ini.set('User Prefs', 'Run', 0)
>>> ini.lines
['[User Prefs]\\n', 'Run=0\\n', 'Show Upgrade Dialog=0\\n']
>>> ini.detect_crlf()
'\\n'
>>> ini.lines.insert(0, '# Comment\\r\\n')
>>> ini.detect_crlf()
'\\r\\n'
"""

__revision__ = "$Rev$"
__date__ = "$Date$"
__author__ = "$Author$"


class IniFile:
    """Very simple .ini file manipulator for Opera."""

    def __init__(self, filename=None):
        self.filename = filename
        if filename is None:
            self.lines = []
        else:
            self.lines = file(filename).readlines()
        self.crlf = self.detect_crlf()

    def detect_crlf(self):
        """Auto-detect end-of-line sequence."""
        if self.lines:
            line = self.lines[0]
        else:
            line = '\n'
        if line[-2:] == '\r\n':
            return line[-2:]
        else:
            return line[-1:]

    def set(self, section, key, value):
        """Change or add a configuration line."""
        key_value_line = '%s=%s%s' % (key, value, self.crlf)
        start, stop = self.find_section(section)
        if start is None:
            # Section not found, append section at the end
            if self.lines and self.lines[-1].strip() == '':
                self.lines.append(self.crlf) # Blank line
            self.lines.append('[%s]%s' % (section, self.crlf))
            self.lines.append(key_value_line)
        else:
            # Find the key line in the section
            index = self.find_key(start, stop, key)
            if index is None:
                # Not found, insert at end of section
                self.lines.insert(stop, key_value_line)
            else:
                # Replace key line with new value
                self.lines[index] = key_value_line

    def find_section(self, section):
        """Find the beginning and end of a configuration section."""
        start = None
        for index, line in enumerate(self.lines):
            if line.strip() == '[%s]' % section:
                start = index
            if start is not None and line.strip() == '':
                return start, index
        return start, len(self.lines)

    def find_key(self, start, stop, key):
        """Find a key inside a configuration section."""
        for index in range(start, stop):
            if self.lines[index].startswith(key + '='):
                return index

    def save(self, filename=None):
        """Write lines back to file."""
        if filename is None:
            filename = self.filename
        if filename is None:
            raise NameError
        open(self.filename, 'w').write(''.join(self.lines))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
