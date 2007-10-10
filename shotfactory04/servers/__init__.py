import platform


class Server:

    def __init__(self, options):
        self.revision = options.revision

    def get_user_agent(self):
        return ' '.join((
            'ShotFactory/0.4', self.revision,
            'Python/%s' % (platform.python_version()),
            '%s/%s' % (platform.system(), platform.release()),
            platform.machine(),
            ))
