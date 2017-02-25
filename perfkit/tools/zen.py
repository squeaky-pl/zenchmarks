import click
import os.path

from perfkit.process import Process


class Zen(Process):
    def __init__(self, binary, connections, time):
        if not binary:
            binary = 'vendor/zen'
        self.binary = binary
        self.connections = connections or 100
        self.time = time or 2

    def configure(self, tested):
        pass

    @property
    def cmd(self):
        options = [
            '-c', str(self.connections),
            '-d', str(self.time)
        ]

        return [
            os.path.abspath(self.binary), *options,
        ]

    def report(self):
        for line in self.output.splitlines():
            if not line.startswith(b'Requests:'):
                continue
            line = line.split()
            rps = float(line[1])
            return rps

    def __repr__(self):
        return '<Zen {} connection(s)>'.format(
            self.connections)


@click.command()
@click.option('--binary')
@click.option('--time', type=int)
@click.option('--connections', type=int)
@click.option('--repeat', type=int)
def cli(binary, time, connections, repeat):
    if repeat:
        return [Zen(binary, connections, time) for _ in range(repeat)]
    else:
        return Zen(binary, connections, time)
