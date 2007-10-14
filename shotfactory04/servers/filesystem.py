import os
import re
import time
from xmlrpclib import Fault
from shotfactory04.servers import Server

EXPIRE_SECONDS = 300 # request lock expiration timeout
LOCKTIME_FORMAT = '%y%m%d-%H%M%S'
INTEGER_KEYS = 'width height bpp major minor'.split()

config_line_match = re.compile(r'(\w+)\s*(.*)').match


class FileSystemServer(Server):

    def __init__(self, options):
        Server.__init__(self, options)
        self.factory = options.factory
        self.queue = options.queue
        self.output = options.output
        self.resize = options.resize_output

    def parse_locktime(self, filename):
        parts = filename.split('-')
        timestamp = '-'.join(parts[-2:])
        try:
            return time.mktime(time.strptime(timestamp, LOCKTIME_FORMAT))
        except ValueError:
            return time.time()

    def get_oldest_filename(self):
        mtimes = []
        expire = time.time() - EXPIRE_SECONDS
        for filename in os.listdir(self.queue):
            fullpath = os.path.join(self.queue, filename)
            if not os.path.isfile(fullpath):
                continue
            if 'locked' in filename:
                locktime = self.parse_locktime(filename)
                if locktime > expire:
                    continue
            try:
                mtime = os.stat(fullpath).st_mtime
            except OSError:
                continue
            mtimes.append((mtime, filename))
        if not len(mtimes):
            return None
        mtimes.sort()
        return mtimes[0][1]

    def poll(self):
        while True:
            oldest = self.get_oldest_filename()
            if oldest is None:
                raise Fault(204, 'No matching request.')
            filename = oldest
            pos = filename.find('-locked-')
            if pos > -1:
                filename = filename[:pos]
            self.request_filename = '-'.join((
                filename, 'locked', self.factory,
                time.strftime(LOCKTIME_FORMAT)))
            fullpath = os.path.join(self.queue, self.request_filename)
            try:
                os.rename(os.path.join(self.queue, oldest), fullpath)
            except OSError:
                continue # Somebody else locked this request already.
            config = {
                'filename': filename,
                'browser': 'Firefox',
                'width': 1024,
                'bpp': 24,
                'command': '',
                }
            for line in open(fullpath).readlines():
                line = line.strip()
                if not len(line):
                    continue
                match = config_line_match(line)
                if match is None:
                    raise Fault(500, 'Bad request line "%s" in %s.' %
                                (line, self.request_filename))
                key, value = match.groups()
                if key in INTEGER_KEYS:
                    value = int(value)
                config[key] = value
            return config

    def get_request_url(self, config):
        return config['url']

    def upload_png(self, config, pngfilename):
        os.unlink(os.path.join(self.queue, self.request_filename))
        if 'request' in config:
            filename = config['request'] + '.png'
        else:
            filename = config['filename'] + '.png'
        for width, folder in self.resize:
            os.system('pngtopnm "%s" | pnmscale -width %d | pnmtopng > "%s"' %
                      (pngfilename, width, os.path.join(folder, filename)))
        if self.output:
            os.rename(pngfilename, os.path.join(self.output, filename))
