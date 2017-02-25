import sys
import os
import signal


sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'vendor')))


from curio import run, tcp_server, spawn, SignalSet

from zenlines import zenlines


async def echo(client, addr):
    data = b''
    while 1:
        data += await client.recv(1024)
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

            await client.sendall(response.encode('ascii'))


async def main():
    server = await spawn(tcp_server('127.0.0.1', 8080, echo))

    await SignalSet(signal.SIGTERM, signal.SIGINT).wait()

    await server.cancel()


run(main())
