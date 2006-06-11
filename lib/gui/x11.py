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

import os, time
from shotfactory03.gui.base import BaseGui
from shotfactory03.image import hashmatch
import png

class X11Gui(BaseGui):
    """
    Special functions for the X11 screen.
    """

    def __init__(self, display=0):
        self.display = display

    def shell(self, command):
        """Run a shell command on my display."""
        return os.system('DISPLAY=:%d %s' % (self.display, command))

    def home(self):
        """Scroll to the top."""
        self.shell('xte "key Home"')

    def end(self):
        """Scroll to the bottom."""
        self.shell('xte "key End"')

    def pageup(self):
        """Scroll up by one screen page."""
        self.shell('xte "key Page_Up"')

    def pagedown(self):
        """Scroll down by one screen page."""
        self.shell('xte "key Page_Down"')

    def up(self):
        """Scroll up by one line."""
        self.shell('xte "key Up"')

    def down(self):
        """Scroll down by one line."""
        self.shell('xte "key Down"')

    def close_window(self):
        """Close the active window."""
        self.shell('xte "keydown Alt_L"')
        self.shell('xte "key F4"')
        self.shell('xte "keyup Alt_L"')

    def maximize(self):
        """Maximize the active window."""
        self.shell('xte "keydown Alt_L"')
        self.shell('xte "key F10"')
        self.shell('xte "keyup Alt_L"')

    def hide_mouse(self):
        """Move the mouse cursor out of the way."""
        self.shell('xte "mousemove 400 0"')

    def screenshot(self, filename):
        """Save the full screen to a PPM file."""
        self.shell('xwd -root -silent | xwdtopnm > "%s"' % filename)

    @staticmethod
    def page_filename(page_number, direction='dn'):
        """Create a PPM filename."""
        return 'pg%s%02d.ppm' % (direction, page_number)

    def scroll_pages(self, good_offset=300):
        """
        Take screenshots and scroll down between them.
        """
        filename = self.page_filename(1)
        pixels_per_line = 50
        scroll_lines = good_offset / pixels_per_line
        offsets = []
        for page in range(2, 20):
            for dummy in range(scroll_lines):
                self.down()
            time.sleep(0.5)

            previous = filename
            filename = self.page_filename(page)
            self.screenshot(filename)
            offset = hashmatch.find_offset(previous, filename)

            apparently = offset / scroll_lines
            if apparently > 10 and apparently != pixels_per_line:
                pixels_per_line = apparently
                scroll_lines = good_offset / pixels_per_line
            if not offset:
                break
            offsets.append(offset)
        return offsets

    def merge(self, width, height, offsets):
        """
        Merge multi-page screenshots and return a string of pixels.
        """
        overlaps = []
        for offset in offsets:
            overlaps.append(height - offset)
        print 'offsets: ', offsets
        print 'overlaps:', overlaps

        pixels = []
        total = 0
        scanline = 3*width
        for index in range(0, len(offsets) + 1):
            top = 0
            bottom = 0
            if index > 0:
                top = overlaps[index-1] / 2
            if index < len(offsets):
                bottom = (overlaps[index]+1) / 2
            segment = height - top - bottom
            total += segment
            bottom = height - bottom
            filename = self.page_filename(index+1)
            print filename, top, bottom, segment, total
            infile = open(filename, 'rb')
            hashmatch.read_ppm_header(infile)
            pixels.append(infile.read()[scanline*top:scanline*bottom])
        return total, ''.join(pixels)

    def browsershot(self, pngfilename = 'browsershot.png'):
        """
        Take a number of screenshots and merge them into one tall image.
        """
        self.hide_mouse()
        time.sleep(0.1)

        filename = self.page_filename(1)
        self.screenshot(filename)
        magic, width, height, maxval = hashmatch.read_ppm_header(open(filename, 'rb'))
        assert magic == 'P6'
        assert maxval == 255

        offsets = self.scroll_pages(good_offset=height/2)
        total, pixels = self.merge(width, height, offsets)

        outfile = file(pngfilename, 'wb')
        png.write(outfile, width, total, pixels, interlace = True)
        outfile.close()
