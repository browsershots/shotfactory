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
        self.shell('xwd -root -silent | xwdtopnm | pnmdepth 255 > "%s"' % filename)

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
            time.sleep(0.1)

            previous = filename
            filename = self.page_filename(page)
            self.screenshot(filename)
            offset = hashmatch.find_offset(previous, filename)

            if not offset:
                break
            offsets.append(offset)

            apparently = offset / scroll_lines
            if apparently == 0:
                print ("apparently no offset per keypress: %d/%d=%d"
                       %(offset, scroll_lines, apparently))
            elif apparently != pixels_per_line:
                pixels_per_line = apparently
                scroll_lines = min(good_offset / pixels_per_line, 40)
                print ("%d pixels/keypress, %d keypresses/scroll"
                       % (pixels_per_line, scroll_lines))
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
