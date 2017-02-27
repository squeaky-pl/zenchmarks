import sys
import os
import signal


sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'vendor')))


from gevent.server import StreamServer
import gevent.signal

from zenlines import zenlines


def echo(socket, address):
    data = b''
    while 1:
        data += socket.recv(1024)
        if not data:
            break

        while 1:
            lead, sep, rest = data.partition(b'\n')
            if not sep:
                break

            data = rest

            try:
                response = zenlines[lead.decode('ascii')] + '\n'
            except KeyError:
                response = 'Not Found\n'

            socket.sendall(response.encode('ascii'))


server = StreamServer(('127.0.0.1', 8080), echo)

def stop_server(signal, frame):
    server.stop()


gevent.signal.signal(signal.SIGTERM, stop_server)
gevent.signal.signal(signal.SIGINT, stop_server)

server.serve_forever()
