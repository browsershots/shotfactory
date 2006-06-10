#!/usr/bin/env python
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
Check formatting of Python source code.
"""

__revision__ = '$Rev$'
__date__ = '$Date$'
__author__ = '$Author$'

import sys

class FormatError:
    """
    The Python file does not comply with the Browsershots file formatting standard.
    """
    def __init__(self, filename, lineno, error):
        self.message = "%s:%d: %s" % (filename, lineno, error)

def read_blocks(filename):
    """
    Read a file and split it into blocks by blank lines.
    """
    blocks = []
    block = []
    start = 1
    docstring = False
    lines = file(filename).readlines()
    if not lines:
        raise FormatError(filename, 1, "empty file")
    if not lines[-1].endswith('\n'):
        raise FormatError(filename, len(lines), 'no newline before EOF')
    if lines[-1].strip() == '':
        raise FormatError(filename, len(lines), 'blank line before EOF')
    lines.append('')
    for number, line in enumerate(lines):
        if line.rstrip('\n') != line.rstrip():
            raise FormatError(filename, number + 1, 'trailing whitespace')
    for number, line in enumerate(lines):
        stripped = line.strip()
        if stripped == '"""' and not docstring:
            stripped = ''
            docstring = True
        if stripped or docstring:
            block.append(line)
        else:
            if block:
                blocks.append([start, block])
                if len(blocks) > 4:
                    break
                block = []
            start = number + 2
        if stripped == '"""' and docstring:
            docstring = False
    return blocks

def remove_shebang(head):
    """
    Remove the first line if it is a valid shebang.
    """
    if head[1][0] == '#!/usr/bin/env python\n':
        head[0] += 1
        head[1].pop(0)

def check_file(filename):
    """
    Read a Python source file and check it for Browsershots formatting.
    Raise FormatError if it doesn't comply.
    """
    blocks = read_blocks(filename)
    if len(blocks) < 3:
        lastblock = blocks[-1]
        raise FormatError(filename, lastblock[0], "missing header, too few paragraphs")
    head, docstring, keywords = blocks[:3]
    remove_shebang(head)
    if head[1] != ref_head[1]:
        for offset, line in enumerate(head[1]):
            if offset >= len(ref_head[1]):
                raise FormatError(filename, head[0] + offset, "copyright too short")
            if line != ref_head[1][offset]:
                raise FormatError(filename, head[0] + offset, "wrong copyright")
        raise FormatError(filename, head[0] + len(head[1]), "copyright too short")
    if docstring[1][0].strip() != '"""':
        raise FormatError(filename, docstring[0], "missing docstring")
    if docstring[1][-1].strip() != '"""':
        raise FormatError(filename, docstring[0] + len(docstring[1]) - 1, "missing docstring")
    if len(docstring[1]) < 3:
        raise FormatError(filename, docstring[0] + 1, "empty docstring")
    if not keywords[1][0].startswith("__revision__ = '$Rev:"):
        raise FormatError(filename, keywords[0], "missing __revision__ = '$Rev:")
    if not keywords[1][1].startswith("__date__ = '$Date:"):
        raise FormatError(filename, keywords[0] + 1, "missing __date__ = '$Date:")
    if not keywords[1][2].startswith("__author__ = '$Author:"):
        raise FormatError(filename, keywords[0] + 2, "missing __author__ = '$Author:")

def check_files(files):
    """
    Check a list of files.
    Exit with error code 1 if any files don't comply.
    """
    error = False
    files.sort()
    for filename in files:
        try:
            check_file(filename)
        except FormatError, instance:
            print instance.message
            error = True
    if error:
        sys.exit(1)

reference = read_blocks(sys.argv[0])
ref_head, ref_docstring, ref_keywords = reference[:3]
remove_shebang(ref_head)
check_files(sys.argv[1:])
