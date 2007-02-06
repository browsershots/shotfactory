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
"""

__revision__ = '$Rev$'
__date__ = '$Date$'
__author__ = '$Author$'


import os, time
from shotfactory03.gui import linux as base


class Gui(base.Gui):
    """
    Special functions for Opera.
    """

    def remove_crash_dialog(self):
        """Delete evidence of previous browser crash."""
        home = os.environ['HOME'].rstrip('/')
        inifile = home + '/.opera/opera6.ini'
        if os.path.exists(inifile):
            print 'removing crash dialog from', inifile
            os.system("sed -i -e 's/^Run=[0-9]$/Run=0/g' " + inifile)
