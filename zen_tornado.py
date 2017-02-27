import sys
import os
import signal


sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'vendor')))


from tornado.tcpserver import TCPServer
from tornado import gen
from tornado.iostream import StreamClosedError
import tornado.ioloop

from zenlines import zenlines


class Zen(TCPServer):
    @gen.coroutine
    def handle_stream(self, stream, address):
        while 1:
            try:
                data = (yield stream.read_until(b'\n')).strip()
            except StreamClosedError:
                break

            try:
                response = zenlines[data.decode('ascii')] + '\n'
            except KeyError:
                response = 'Not Found\n'

            yield stream.write(response.encode('ascii'))


server = Zen()
server.listen(8080)

loop = tornado.ioloop.IOLoop.current()


def stop(signal, frame):
    server.stop()
    loop.stop()


signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGINT, stop)

loop.start()
