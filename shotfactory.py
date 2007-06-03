#!/usr/bin/env python
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
Screenshot factory.
"""

__revision__ = "$Rev$"
__date__ = "$Date$"
__author__ = "$Author$"

import sys
import os
import time
import xmlrpclib
import socket
import platform
import re
import traceback
from md5 import md5


pngfilename = 'browsershot.png'
# Security: allow only alphanumeric browser commands
# Optionally within a subfolder, relative to working directory
safe_command = re.compile(r'^([\w_\-]+[\\/])*[\w_\-\.]+$').match


def log(status, extra=None):
    """
    Add a line to the log file.
    """
    logfile = open('shotfactory.log', 'a')
    logfile.write(time.strftime('%Y-%m-%d %H:%M:%S'))
    logfile.write(' ')
    logfile.write(status)
    if extra is not None:
        logfile.write(' ')
        logfile.write(str(extra))
    logfile.write('\n')
    logfile.close()


def sleep():
    """Sleep a while to wait for new requests."""
    time.sleep(60)


def crypt_password(challenge, password, prefix = ''):
    """
    Encrypt a password for transmission.
    """
    salt = challenge[:4]
    nonce = challenge[4:]
    crypt = md5(salt + password).hexdigest()
    crypt = md5(prefix + crypt + nonce).hexdigest()
    return crypt


def import_deep(name, parent_levels=0):
    """
    Import a module from some.levels.deep and return the module
    itself, not its uppermost parent. If the module is unavailable,
    try its parents, up to parent_levels. The default of 0 means no
    parents are tried.
    """
    parts = name.split('.')
    while len(parts) and parent_levels >= 0:
        try:
            print "trying to import", name
            module = __import__(name)
            for part in parts[1:]:
                module = getattr(module, part)
            return module
        except ImportError:
            parts.pop()
            name = '.'.join(parts)
            if parent_levels > 0:
                parent_levels -= 1
            else:
                raise


def browsershot(options, server, config, challenge, password):
    """
    Process a screenshot request and upload the resulting PNG file.
    """
    platform_name = platform.system()
    if platform_name in ('Microsoft', 'Microsoft Windows'):
        platform_name = 'Windows'
    if platform_name in ('Linux', 'Darwin', 'Windows'):
        module_name = 'shotfactory03.gui.%s.%s' % (
            platform_name.lower(),
            config['browser'].lower())
    else:
        raise NotImplementedError("unsupported platform: " + platform_name)
    gui_module = import_deep(module_name, parent_levels=1)
    gui = gui_module.Gui(config, options)

    # Close old browser instances and helper programs
    gui.close()

    # Reset browser (delete cache etc.)
    if hasattr(gui, 'reset_browser'):
        gui.reset_browser()
    else:
        print "reset_browser() method is missing in", module_name

    # Prepare screen for output
    gui.prepare_screen()

    # Start new browser
    crypt = crypt_password(challenge, password, 'redirect')
    url = '/'.join((options.server, 'redirect', crypt,
                    str(config['request'])))
    gui.start_browser(config, url, options)

    # Make screenshots
    if os.path.exists(pngfilename):
        os.remove(pngfilename)
    gui.browsershot(pngfilename)

    # Close browser and helper programs
    gui.close()

    # Upload PNG file
    binary_file = file(pngfilename, 'rb')
    binary_data = binary_file.read()
    binary = xmlrpclib.Binary(binary_data)
    binary_file.close()
    crypt = crypt_password(challenge, password)
    upload_started = time.time()
    status, challenge = server.request.upload(binary, crypt)
    seconds = time.time() - upload_started
    if status == 'OK':
        bytes = len(binary_data) * 8 / 6 # base64 encoding
        print "uploaded %d bytes in %.2f seconds (%.2f kbps)" % (
            bytes, seconds, 8 * bytes / seconds / 1000.0)
        os.remove(pngfilename)
    else:
        status += " (after %.2f seconds)" % seconds
        print "upload failed: " + status
        log(status, config)
    return challenge


def debug_factory_features(server, factory):
    """
    Print the SQL WHERE clause for a given factory, with linebreaks.
    """
    features = server.factory.features(factory)
    start = 0
    nested = 0
    for index in range(len(features)):
        if features[index] == '(':
            nested += 1
            if nested <= 2 and index > 0:
                stop = index
                print features[start:stop].strip()
                start = stop
        elif features[index] == ')':
            nested -= 1
            if nested == 0 and features[index - 1] == ')':
                stop = index
                print features[start:stop].strip()
                start = stop
    rest = features[start:].strip()
    if rest:
        print rest


def error_sleep(message):
    """
    Log error message, sleep a while, get a new challenge.
    """
    if not message:
        message = 'runtime error'
    if not message[0].isupper():
        message = message[0].upper() + message[1:]
    if not message.endswith('.'):
        message += '.'
    print message
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


class ProxyTransport(xmlrpclib.Transport):

    def __init__(self, proxy):
        if hasattr(xmlrpclib.Transport, '__init__'):
            xmlrpclib.Transport.__init__(self)
        self.proxy = proxy

    def make_connection(self, host):
        self.realhost = host
        import httplib
        return httplib.HTTP(self.proxy)

    def send_request(self, connection, handler, request_body):
        connection.putrequest("POST", 'http://%s%s' % (self.realhost, handler))

    def send_host(self, connection, host):
        connection.putheader('Host', self.realhost)


def _main():
    """
    Main loop for screenshot factory.
    """
    from optparse import OptionParser
    version = '%prog ' + __revision__.strip('$').replace('Rev: ', 'r')
    parser = OptionParser(version=version)
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                      help="more output (for trouble-shooting)")
    parser.add_option("-p", dest="password", action="store", type="string",
                      metavar="<password>",
                      help="supply password on command line (insecure)")
    parser.add_option("-s", dest="server", action="store", type="string",
                      metavar="<url>", default="http://browsershots.org",
                      help="server url (default: http://browsershots.org)")
    parser.add_option("-f", dest="factory", action="store", type="string",
                      metavar="<name>",
                      help="factory name (default: hostname)")
    parser.add_option("-P", dest="proxy", action="store", type="string",
                      metavar="<proxy>",
                      help="use a HTTP proxy (default: environment)")
    parser.add_option("-d", dest="display", action="store", type="string",
                      metavar="<name>", default=":1",
                      help="run on a different display (default: :1)")
    parser.add_option("-l", dest="loadlimit", action="store", type="float",
                      metavar="<limit>", default=1.0,
                      help="system load limit (default: 1.0)")
    parser.add_option("-w", dest="wait", action="store", type="int",
                      metavar="<seconds>", default=30,
                      help="wait while page is loading (default: 30)")
    (options, args) = parser.parse_args()

    if options.password is None:
        from getpass import getpass
        options.password = getpass('Factory password: ')

    if options.factory is None:
        options.factory = socket.gethostname()
        dot = options.factory.find('.')
        if dot > -1:
            options.factory = options.factory[:dot]

    if options.proxy is None:
        if 'http_proxy' in os.environ:
            options.proxy = os.environ['http_proxy']

    socket.setdefaulttimeout(180.0)
    if options.proxy:
        server = xmlrpclib.Server(options.server,
            transport=ProxyTransport(options.proxy))
    else:
        server = xmlrpclib.Server(options.server)
    challenge = server.auth.challenge(options.factory)
    crypt = crypt_password(challenge, options.password)
    auth_test = server.auth.test(options.factory, crypt)
    if not auth_test == 'OK':
        print auth_test
        sys.exit(1)

    debug_factory_features(server, options.factory)
    challenge = None
    while True:
        try:
            load = systemload()
            if load > options.loadlimit:
                challenge = None
                error_sleep('system load %.2f exceeds limit %.2f, sleeping' %
                            (load, options.loadlimit))
                continue
            print '=' * 32, time.strftime('%H:%M:%S'), '=' * 32
            if not challenge:
                challenge = server.auth.challenge(options.factory)
            print 'challenge:', challenge
            crypt = crypt_password(challenge, options.password)
            challenge = None

            poll_start = time.time()
            status, challenge, config = server.request.poll(
                options.factory, crypt)
            poll_latency = time.time() - poll_start
            print 'server poll latency: %.2f seconds' % poll_latency

            if status == 'OK':
                print config
                if not safe_command(config['command']):
                    raise RuntimeError(
                        'unsafe command "%s"' % config['command'])
                challenge = browsershot(options, server, config,
                                        challenge, options.password)
            elif status == 'No matching request.':
                print status
                sleep()
            else:
                error_sleep(status)
                challenge = None
        except xmlrpclib.ProtocolError:
            error_sleep('XML-RPC protocol error.')
            challenge = None
        except socket.gaierror, (errno, message):
            error_sleep('Socket gaierror: ' + message)
            challenge = None
        except socket.timeout:
            error_sleep('Socket timeout.')
            challenge = None
        except socket.error, error:
            if type(error.args) in (tuple, list):
                (errno, message) = error.args
            else:
                message = str(error.args)
            error_sleep('Socket error: ' + message)
            challenge = None
        except RuntimeError, message:
            if options.verbose:
                traceback.print_exc()
            error_sleep(str(message))
            challenge = None


if __name__ == '__main__':
    _main()
