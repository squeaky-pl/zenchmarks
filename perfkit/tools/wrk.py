import click
import os.path

from perfkit.process import Process


class Wrk(Process):
    def __init__(self, binary, script, time):
        if not binary:
            binary = 'vendor/wrk'
        self.binary = binary
        self.host = None
        self.port = None
        self.connections = 100
        self.rate = 100
        self.threads = 1
        self.time = time or 2
        self.script = script

    def configure(self, tested):
        self.host, self.port = tested.psprocess.connections()[0].laddr

    @property
    def cmd(self):
        options = [
            "-R", str(self.rate),
            '-c', str(self.connections),
            '-t', str(self.threads),
            '-d', str(self.time)
        ]
        if self.script:
            options.extend(['-s', self.script])

        return [
            os.path.abspath(self.binary), *options,
            'http://{}:{}'.format(self.host, self.port)]

    def report(self):
        for line in self.output.splitlines():
            if not line.startswith(b'Requests/sec:'):
                continue
            line = line.split()
            rps = float(line[1])
            return rps

    def __repr__(self):
        return '<Wrk {}:{} {} threads(s) {} connection(s)>'.format(
            self.host, self.port, self.threads, self.connections)


@click.command()
@click.option('--binary')
@click.option('--time', type=int)
@click.option('--script')
@click.option('--repeat', type=int)
def cli(binary, time, script, repeat):
    if repeat:
        return [Wrk(binary, script, time) for _ in range(repeat)]
    else:
        return Wrk(binary, script, time)
