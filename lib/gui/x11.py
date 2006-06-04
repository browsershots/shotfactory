# -*- coding: utf-8 -*-
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

import os
from shotfactory03.gui.base import BaseGui

class X11Gui(BaseGui):
    """
    Special functions for the X11 screen.
    """

    @staticmethod
    def home():
        """Scroll to the top."""
        os.system('xte "key Home"')

    @staticmethod
    def end():
        """Scroll to the bottom."""
        os.system('xte "key End"')

    @staticmethod
    def pageup():
        """Scroll up by one screen page."""
        os.system('xte "key Page_Up"')

    @staticmethod
    def pagedown():
        """Scroll down by one screen page."""
        os.system('xte "key Page_Down"')

    @staticmethod
    def up():
        """Scroll up by one line."""
        os.system('xte "key Up"')

    @staticmethod
    def down():
        """Scroll down by one line."""
        os.system('xte "key Down"')

    @staticmethod
    def hide_mouse():
        """Move the mouse cursor out of the way."""
        os.system('xte "mousemove 400 0"')

    @staticmethod
    def screenshot(filename):
        """Save the full screen to a PPM file."""
        os.system('xwd -root -silent | xwdtopnm > "%s"' % filename)
