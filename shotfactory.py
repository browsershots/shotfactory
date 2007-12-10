#!/usr/bin/env python
# browsershots.org - Test your web design in different browsers
# Copyright (C) 2007 Johann C. Rocholl <johann@browsershots.org>
#
# Browsershots is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Browsershots is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
Screenshot factory.
"""

__revision__ = "$Rev$"
__date__ = "$Date$"
__author__ = "$Author$"

import sys
import os
import time
import re
import socket
import platform
import traceback
import xmlrpclib

default_server_url = 'http://api.browsershots.org/'

# Security: allow only alphanumeric browser commands
# Optionally within a subfolder, relative to working directory
safe_command = re.compile(r'^([\w_\-]+[\\/])*[\w_\-\.]+$').match


def log(message, extra=None):
    """
    Add a line to the log file.
    """
    logfile = open('shotfactory.log', 'a')
    logfile.write(time.strftime('%Y-%m-%d %H:%M:%S'))
    logfile.write(' ')
    logfile.write(message)
    if extra is not None:
        logfile.write(' ')
        logfile.write(str(extra))
    logfile.write('\n')
    logfile.close()


def sleep():
    """Sleep a while to wait for new requests."""
    time.sleep(60)


def browsershot(options, server, config, password):
    """
    Process a screenshot request and upload the resulting PNG file.
    """
    browser_module = config['browser'].lower()
    if browser_module == 'internet explorer':
        browser_module = 'msie'
    platform_name = platform.system()
    if platform_name in ('Microsoft', 'Microsoft Windows'):
        platform_name = 'Windows'
    if platform_name in ('Linux', 'Darwin', 'Windows'):
        module_name = 'shotfactory04.gui.%s.%s' % (
            platform_name.lower(), browser_module)
    else:
        raise NotImplementedError("unsupported platform: " + platform_name)
    gui_module = __import__(module_name, globals(), locals(), ['non-empty'])
    gui = gui_module.Gui(config, options)

    # Close old browser instances and helper programs
    gui.close()

    # Reset browser (delete cache etc.)
    gui.reset_browser()

    # Prepare screen for output
    gui.prepare_screen()

    # Start new browser
    url = server.get_request_url(config)
    gui.start_browser(config, url, options)

    # Make screenshots
    pngfilename = '%s.png' % config['request']
    if os.path.exists(pngfilename):
        os.remove(pngfilename)
    gui.browsershot(pngfilename)

    # Close browser and helper programs
    gui.close()

    # Upload PNG file
    bytes = server.upload_png(config, pngfilename)
    if os.path.exists(pngfilename):
        os.remove(pngfilename)
    return bytes


def error_sleep(message):
    """
    Log error message, sleep a while.
    """
    if not message:
        message = "runtime error"
    if not message[0].isupper():
        message = message[0].upper() + message[1:]
    if not message.endswith('.'):
        message += '.'
    print message
    if not message.startswith('204 '):
        log(message)
    sleep()


def systemload():
    """
    Try to get the number of processes in the system run queue,
    averaged over the last minute. If this info is unavailable,
    return None.
    """
    try:
        return max(os.getloadavg())
    except (AttributeError, OSError):
        return None


def check_dir(parser, dirname):
    if not os.path.exists(dirname):
        parser.error("directory doesn't exist: %s" % dirname)
    if not os.path.isdir(dirname):
        parser.error("not a directory: %s" % dirname)
    if not os.access(dirname, os.R_OK):
        parser.error("directory not readable: %s" % dirname)
    if not os.access(dirname, os.W_OK):
        parser.error("directory not writable: %s" % dirname)


def _main():
    """
    Main loop for screenshot factory.
    """
    from optparse import OptionParser
    revision = __revision__.strip('$').replace('Rev: ', 'r')
    version = '%prog ' + revision
    parser = OptionParser(version=version)
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
                      help="more output (for trouble-shooting)")
    parser.add_option('-p', '--password', action='store', type='string',
                      metavar='<password>',
                      help="supply password on command line (insecure)")
    parser.add_option('-s', '--server', action='store', type='string',
                      metavar='<url>', default=default_server_url,
                      help="server url (%s)" % default_server_url)
    parser.add_option('-f', '--factory', action='store', type='string',
                      metavar='<name>',
                      help="factory name (default: hostname)")
    parser.add_option('-P', '--proxy', action='store', type='string',
                      metavar='<proxy>',
                      help="use a HTTP proxy (default: environment)")
    parser.add_option('-d', '--display', action='store', type='string',
                      metavar='<name>', default=':1',
                      help="run on a different display (default: :1)")
    parser.add_option('-w', '--wait', action='store', type='int',
                      metavar='<seconds>', default=30,
                      help="wait while page is loading (default: 30)")
    parser.add_option('-l', '--load-limit', action='store', type='float',
                      metavar='<limit>', default=1.0,
                      help="system load limit (default: 1.0)")
    parser.add_option('-u', '--upload-limit', action='store', type='float',
                      metavar='<megabytes>', default=100,
                      help="maximum megabytes per hour (default: 100)")
    parser.add_option('-q', '--queue', action='store', type='string',
                      metavar='<directory>',
                      help="get requests from files, don't poll server")
    parser.add_option('-o', '--output', action='store', type='string',
                      metavar='<directory>',
                      help="save screenshots locally, don't upload")
    parser.add_option('-r', '--resize-output', action='append', nargs=2,
                      metavar='<width> <folder>', default=[],
                      help="scale screenshots and save locally")
    parser.add_option('-m', '--max-pages', action='store', type='int',
                      metavar='<count>', default=7,
                      help="scroll down and merge screenshots (default: 7)")
    (options, args) = parser.parse_args()
    options.revision = revision

    if options.factory is None:
        options.factory = socket.gethostname().split('.')[0].lower()

    if options.queue and (options.output or options.resize_output):
        options.server = None
        options.queue = os.path.abspath(options.queue)
        check_dir(parser, options.queue)
        if options.output:
            options.output = os.path.abspath(options.output)
            check_dir(parser, options.output)
        for index in range(len(options.resize_output)):
            width, folder = options.resize_output[index]
            width = int(width)
            folder = os.path.abspath(folder)
            check_dir(parser, folder)
            options.resize_output[index] = (width, folder)
        from shotfactory04.servers.filesystem import FileSystemServer
        server = FileSystemServer(options)
    elif options.queue:
        parser.error("--queue also requires --output or --resize-output")
    elif options.output:
        parser.error("--output also requires --queue")
    elif options.resize_output:
        parser.error("--resize-output also requires --queue")
    else:
        options.queue = None
        options.output = None
        if not options.server.startswith('http://'):
            options.server = 'http://' + options.server
        if options.password is None:
            from getpass import getpass
            options.password = getpass('Factory password: ')
        if options.proxy is None:
            if 'http_proxy' in os.environ:
                options.proxy = os.environ['http_proxy']
        from shotfactory04.servers.xmlrpc import XMLRPCServer
        server = XMLRPCServer(options)
        if options.verbose:
            server.debug_factory_features()

    upload_log = []
    while True:
        try:
            load = systemload()
            if load > options.load_limit:
                error_sleep("system load %.2f exceeds limit %.2f, sleeping" %
                            (load, options.load_limit))
                continue
            one_hour_ago = time.time() - 3600
            upload_log = [log for log in upload_log if log[0] > one_hour_ago]
            if upload_log:
                bytes_uploaded = sum([log[1] for log in upload_log])
                seconds = max(60, time.time() - upload_log[0][0])
                bytes_per_hour = bytes_uploaded / seconds * 3600
                if bytes_per_hour > options.upload_limit * 1024 * 1024:
                    error_sleep(' '.join((
"estimated %.2f MB per hour" % (bytes_per_hour / 1024.0 / 1024.0),
"exceeds upload limit %.2f MB, sleeping" % options.upload_limit)))
                    continue
            print '=' * 32, time.strftime('%H:%M:%S'), '=' * 32
            config = server.poll()
            print config
            if config['command'] and not safe_command(config['command']):
                raise RuntimeError("unsafe command '%s'" % config['command'])
            bytes = browsershot(options, server, config, options.password)
            upload_log.append((time.time(), bytes))
        except socket.gaierror, (errno, message):
            error_sleep("Socket gaierror: " + message)
        except socket.timeout:
            error_sleep("Socket timeout.")
        except socket.error, error:
            if type(error.args) in (tuple, list):
                (errno, message) = error.args
            else:
                message = str(error.args)
            error_sleep("Socket error: " + message)
        except xmlrpclib.ProtocolError:
            error_sleep("XML-RPC protocol error.")
        except xmlrpclib.Fault, fault:
            error_sleep("%d %s" % (fault.faultCode, fault.faultString))
        except RuntimeError, message:
            if options.verbose:
                traceback.print_exc()
            error_sleep(str(message))


if __name__ == '__main__':
    _main()
