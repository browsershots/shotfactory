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
Base class for GUI-specific wrappers.
"""

__revision__ = "$Rev$"
__date__ = "$Date$"
__author__ = "$Author$"

import time
import os
from array import array
from shotfactory03.image import hashmatch, png


class Gui:
    """
    Base class for all GUI wrappers.
    """

    def __init__(self, config, options):
        """
        Save settings for internal use later.
        """
        self.width = config['width']
        if not self.width:
            self.width = 1024
        if self.width == 1280:
            self.height = 1024
        else:
            self.height = self.width / 4 * 3
        self.bpp = config['bpp']
        if not self.bpp:
            self.bpp = 24
        self.dpi = 90
        if hasattr(options, 'display'):
            self.display = options.display
        self.top_skip = 0
        self.bottom_skip = 0

    def page_filename(self, page_number, direction='dn'):
        """Create a PPM filename."""
        return 'pg%s%02d.ppm' % (direction, page_number)

    def check_screenshot(self, filename):
        """
        Check if the screenshot file looks ok.
        """
        if not os.path.exists(filename):
            raise RuntimeError('screenshot file %s not found' % filename)
        if not os.path.getsize(filename):
            raise RuntimeError('screenshot file %s is empty' % filename)

    def scroll_pages(self, good_offset=300):
        """
        Take screenshots and scroll down between them.
        """
        filename = self.page_filename(1)
        pixels_per_line = 100
        scroll_lines = max(1, good_offset / pixels_per_line)
        offsets = []
        for page in range(2, 7):
            if hasattr(self, 'scroll_down'):
                self.scroll_down(good_offset)
            else:
                for dummy in range(scroll_lines):
                    self.down()
            time.sleep(0.5)

            previous = filename
            filename = self.page_filename(page)
            self.screenshot(filename)
            self.check_screenshot(filename)
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
                scroll_lines = max(1, min(good_offset / pixels_per_line, 40))
                print ("%d pixels/keypress, %d keypresses/scroll"
                       % (pixels_per_line, scroll_lines))
        return offsets

    def scanlines(self, width, height, offsets):
        """
        Merge multi-page screenshots and yield scanlines.
        """
        overlaps = []
        for offset in offsets:
            overlaps.append(height - offset)
        print 'offsets: ', offsets
        print 'overlaps:', overlaps
        total = 0
        row_bytes = 3*width
        for index in range(0, len(overlaps) + 1):
            top = 0
            bottom = 0
            if index == 0:
                top = self.top_skip
            else:
                top = overlaps[index-1] / 2
            if index == len(offsets):
                bottom = self.bottom_skip
            else:
                bottom = (overlaps[index]+1) / 2
            bottom = height - bottom
            segment = bottom - top
            total += segment
            filename = self.page_filename(index+1)
            print filename, top, bottom, segment, total
            infile = open(filename, 'rb')
            hashmatch.read_ppm_header(infile)
            infile.seek(top*row_bytes, 1)
            for y in range(top, bottom):
                scanline = array('B')
                scanline.fromfile(infile, row_bytes)
                yield scanline
            infile.close()

    def browsershot(self, pngfilename = 'browsershot.png'):
        """
        Take a number of screenshots and merge them into one tall image.
        """
        filename = self.page_filename(1)
        self.screenshot(filename)
        self.check_screenshot(filename)
        magic, width, height, maxval = hashmatch.read_ppm_header(
            open(filename, 'rb'))
        assert magic == 'P6'
        assert maxval == 255

        offsets = self.scroll_pages(good_offset=height/2)
        total = height + sum(offsets) - self.top_skip - self.bottom_skip
        print 'total:', total
        scanlines = self.scanlines(width, height, offsets)

        outfile = file(pngfilename, 'wb')
        writer = png.Writer(width, total)
        writer.write(outfile, scanlines)
        outfile.close()
