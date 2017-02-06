import subprocess


class Process:
    def start(self):
        print('Running:', ' '.join(self.cmd))
        self.process = subprocess.Popen(
            self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def stop(self):
        self.process.terminate()
        self.process.wait()

    def wait(self):
        self.process.wait()

    @property
    def output(self):
        if not hasattr(self, '_output'):
            self._output = self.process.stdout.read()

        return self._output

    @property
    def exitcode(self):
        return self.process.returncode
