#!/usr/bin/env python
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
Write PNG files in pure Python.
"""

__revision__ = '$Rev$'
__date__ = '$Date$'
__author__ = '$Author$'

import sys, zlib, struct

def write_chunk(outfile, tag, data):
    """
    Write a PNG chunk to the output file, including length and checksum.
    http://www.w3.org/TR/PNG/#5Chunk-layout
    """
    outfile.write(struct.pack("!I", len(data)))
    outfile.write(tag)
    outfile.write(data)
    checksum = zlib.crc32(tag)
    checksum = zlib.crc32(data, checksum)
    outfile.write(struct.pack("!I", checksum))

def write(outfile, width, height, pixels, interlaced = False):
    """
    Write a 8bpp RGB opaque PNG file to the output file.
    http://www.w3.org/TR/PNG/
    """
    # http://www.w3.org/TR/PNG/#5PNG-file-signature
    outfile.write(struct.pack("8B", 137, 80, 78, 71, 13, 10, 26, 10))
    # http://www.w3.org/TR/PNG/#11IHDR
    if interlaced:
        write_chunk(outfile, 'IHDR', struct.pack("!2I5B", width, height, 8, 2, 0, 0, 1))
    else:
        write_chunk(outfile, 'IHDR', struct.pack("!2I5B", width, height, 8, 2, 0, 0, 0))
    # http://www.w3.org/TR/PNG/#11IDAT
    write_chunk(outfile, 'IDAT', zlib.compress(pixels, 9))
    # http://www.w3.org/TR/PNG/#11IEND
    write_chunk(outfile, 'IEND', '')

def interlace(width, height, pixels):
    """
    Interlace pixel data into 7 consecutive passes.
    http://www.w3.org/TR/PNG/#8Interlace
    """
    result = []
    passes = [(0, 0, 8, 8),
              (4, 0, 8, 8),
              (0, 4, 4, 8),
              (2, 0, 4, 4),
              (0, 2, 2, 4),
              (1, 0, 2, 2),
              (0, 1, 1, 2)]
    scanline = 1+3*width
    for xstart, ystart, xstep, ystep in passes:
        for y in range(ystart, height, ystep):
            if xstart < width:
                result.append(chr(0))
            for x in range(xstart, width, xstep):
                offset = 1 + scanline*y + 3*x
                result.append(pixels[offset:offset+3])
    return ''.join(result)

if __name__ == '__main__':
    write(sys.stdout, 1, 1, interlace(1, 1, chr(0) + 'abc'))
