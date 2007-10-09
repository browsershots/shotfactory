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
import xmlrpclib
import socket
import platform
import re
import traceback
from md5 import md5
from sha import sha
from xmlrpclib import Fault

pngfilename = 'browsershot.png'
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


def encrypt_password(challenge, password):
    """
    Encrypt a password for transmission.
    """
    if challenge['algorithm'] == 'md5':
        inner = md5(challenge['salt'] + password).hexdigest()
    elif challenge['algorithm'] == 'sha1':
        inner = sha(challenge['salt'] + password).hexdigest()
    else:
        raise NotImplemented(
            "Password encryption algorithm '%s' not implemented." %
            challenge['algorithm'])
    return md5(inner + challenge['nonce']).hexdigest()


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
    if hasattr(gui, 'reset_browser'):
        gui.reset_browser()
    else:
        print "reset_browser() method is missing in", module_name

    # Prepare screen for output
    gui.prepare_screen()

    # Start new browser
    challenge = server.nonces.challenge(options.factory)
    encrypted = encrypt_password(challenge, password)
    url = '/'.join((options.server.rstrip('/'), 'redirect',
                    options.factory, encrypted, str(config['request']), ''))
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
    challenge = server.nonces.challenge(options.factory)
    encrypted = encrypt_password(challenge, password)
    upload_started = time.time()
    server.screenshots.upload(
        options.factory, encrypted, config['request'], binary)
    seconds = time.time() - upload_started
    bytes = len(binary_data) * 8 / 6 # base64 encoding
    print "uploaded %d bytes in %.2f seconds (%.2f kbps)" % (
        bytes, seconds, 8 * bytes / seconds / 1000.0)
    os.remove(pngfilename)


def debug_factory_features(features):
    """
    Print the SQL WHERE clause for a given factory, with linebreaks.
    """
    start = 0
    nested = 0
    for index in range(len(features)):
        if features[index] == '(':
            nested += 1
            if nested <= 4 and index > 0:
                print features[start:index].strip()
                start = index
        elif features[index] == ')':
            nested -= 1
            if nested == 0 and features[index - 1] == ')':
                print features[start:index].strip()
                start = index
    rest = features[start:].strip()
    if rest:
        print rest


def error_sleep(message):
    """
    Log error message, sleep a while.
    """
    if not message:
        message = 'runtime error'
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


def user_agent():
    return ' '.join((
        'ShotFactory/0.4',
        'r%s' % __revision__.strip('$').replace('Rev:', '').strip(),
        'Python/%s' % (platform.python_version()),
        '%s/%s' % (platform.system(), platform.release()),
        platform.machine(),
        ))


def _main():
    """
    Main loop for screenshot factory.
    """
    from optparse import OptionParser
    version = '%prog ' + __revision__.strip('$').replace('Rev: ', 'r')
    parser = OptionParser(version=version)
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                      help="more output (for trouble-shooting)")
    parser.add_option("-p", "--password", action="store", type="string",
                      metavar="<password>",
                      help="supply password on command line (insecure)")
    parser.add_option("-s", "--server", action="store", type="string",
                      metavar="<url>", default=default_server_url,
                      help="server url (%s)" % default_server_url)
    parser.add_option("-f", "--factory", action="store", type="string",
                      metavar="<name>",
                      help="factory name (default: hostname)")
    parser.add_option("-P", "--proxy", action="store", type="string",
                      metavar="<proxy>",
                      help="use a HTTP proxy (default: environment)")
    parser.add_option("-d", "--display", action="store", type="string",
                      metavar="<name>", default=":1",
                      help="run on a different display (default: :1)")
    parser.add_option("-l", "--loadlimit", action="store", type="float",
                      metavar="<limit>", default=1.0,
                      help="system load limit (default: 1.0)")
    parser.add_option("-w", "--wait", action="store", type="int",
                      metavar="<seconds>", default=30,
                      help="wait while page is loading (default: 30)")
    (options, args) = parser.parse_args()

    if options.password is None:
        from getpass import getpass
        options.password = getpass('Factory password: ')
    if options.factory is None:
        options.factory = socket.gethostname().split('.')[0].lower()
    if options.proxy is None:
        if 'http_proxy' in os.environ:
            options.proxy = os.environ['http_proxy']
    if not options.server.startswith('http://'):
        options.server = 'http://' + options.server

    socket.setdefaulttimeout(180.0)
    xmlrpc_url = options.server.rstrip('/') + '/xmlrpc/'
    if options.proxy:
        transport = ProxyTransport(options.proxy)
    else:
        transport = xmlrpclib.Transport()
    transport.user_agent = user_agent()
    server = xmlrpclib.Server(xmlrpc_url, transport)
    challenge = server.nonces.challenge(options.factory)
    encrypted = encrypt_password(challenge, options.password)
    server.nonces.verify(options.factory, encrypted)

    features = server.factories.features(options.factory)
    if options.verbose:
        debug_factory_features(features)

    while True:
        try:
            load = systemload()
            if load > options.loadlimit:
                error_sleep('system load %.2f exceeds limit %.2f, sleeping' %
                            (load, options.loadlimit))
                continue
            print '=' * 32, time.strftime('%H:%M:%S'), '=' * 32
            challenge = server.nonces.challenge(options.factory)
            encrypted = encrypt_password(challenge, options.password)

            poll_start = time.time()
            try:
                config = server.requests.poll(options.factory, encrypted)
            finally:
                poll_latency = time.time() - poll_start
                print 'server poll latency: %.2f seconds' % poll_latency

            print config
            if config['command'] and not safe_command(config['command']):
                raise RuntimeError(
                    'unsafe command "%s"' % config['command'])
            browsershot(options, server, config, options.password)
        except xmlrpclib.ProtocolError:
            error_sleep('XML-RPC protocol error.')
        except socket.gaierror, (errno, message):
            error_sleep('Socket gaierror: ' + message)
        except socket.timeout:
            error_sleep('Socket timeout.')
        except socket.error, error:
            if type(error.args) in (tuple, list):
                (errno, message) = error.args
            else:
                message = str(error.args)
            error_sleep('Socket error: ' + message)
        except Fault, fault:
            error_sleep('%d %s' % (fault.faultCode, fault.faultString))
        except RuntimeError, message:
            if options.verbose:
                traceback.print_exc()
            error_sleep(str(message))


if __name__ == '__main__':
    _main()
