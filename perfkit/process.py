import subprocess


class Process:
    def start(self):
        print('Running:', ' '.join(self.cmd))
        self.process = subprocess.Popen(self.cmd)

    def stop(self):
        self.process.terminate()
        self.process.wait()

    def wait(self):
        self.process.wait()

    @property
    def output(self):
        pass

    @property
    def exitcode(self):
        return self.process.returncode
