import click
import sys
import psutil
import time
import os.path


from perfkit.process import Process


class Python(Process):
    def __init__(self, binary, script):
        self.script = script
        self.binary = binary or sys.executable

    @property
    def cmd(self):
        return [os.path.abspath(self.binary), self.script]

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
@click.option('--binary')
def cli(binary, script):
    return Python(binary, script)
