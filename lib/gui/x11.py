# Copyright (C) 2006 Johann C. Rocholl <johann@browsershots.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
    def close_window():
        """Close the active window."""
        os.system('xte "keydown Alt_L"')
        os.system('xte "key F4"')
        os.system('xte "keyup Alt_L"')

    @staticmethod
    def hide_mouse():
        """Move the mouse cursor out of the way."""
        os.system('xte "mousemove 400 0"')

    @staticmethod
    def screenshot(filename):
        """Save the full screen to a PPM file."""
        os.system('xwd -root -silent | xwdtopnm > "%s"' % filename)
