from shotfactory04.servers import Server


class FileSystemServer(Server):

    def __init__(self, options):
        Server.__init__(self, options)
        self.queue = options.queue
        self.output = options.output
