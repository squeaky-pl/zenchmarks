import click
import sys
import psutil
import time


from perfkit.process import Process


class Python(Process):
    def __init__(self, script):
        self.script = script
        self.python = sys.executable
        self.cmd = [self.python, script]

    @property
    def psprocess(self):
        if not getattr(self, '_psprocess', None):
            self._psprocess = psutil.Process(self.process.pid)

        return self._psprocess

    def ready(self):
        while 1:
            if self.psprocess.connections():
                break
            time.sleep(.1)

    def __repr__(self):
        return '<Python {}>'.format(self.script)


@click.command()
@click.argument('script')
def cli(script):
    return Python(script)
