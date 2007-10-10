import os
import re
from xmlrpclib import Fault
from shotfactory04.servers import Server

INTEGER_KEYS = 'request width height bpp major minor'.split()

config_line_match = re.compile(r'(\w+)\s*(.*)').match


class FileSystemServer(Server):

    def __init__(self, options):
        Server.__init__(self, options)
        self.factory = options.factory
        self.queue = options.queue
        self.output = options.output

    def get_oldest_filename(self):
        mtimes = []
        for filename in os.listdir(self.queue):
            fullpath = os.path.join(self.queue, filename)
            if not os.path.isfile(fullpath):
                continue
            if 'locked' in filename:
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
            self.request_filename = oldest + '-locked-' + self.factory
            fullpath = os.path.join(self.queue, self.request_filename)
            try:
                os.rename(os.path.join(self.queue, oldest), fullpath)
            except OSError:
                continue # Somebody else locked this request already.
            config = {}
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
            if 'width' not in config: config['width'] = 1024
            if 'bpp' not in config: config['bpp'] = 24
            return config

    def get_request_url(self, config):
        return config['url']
