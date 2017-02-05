import asyncio
import signal


class Echo(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, exception):
        pass

    def data_received(self, data):
        self.transport.write(data)

#import uvloop
#loop = uvloop.new_event_loop()
loop = asyncio.get_event_loop()
server_coro = loop.create_server(Echo, '0.0.0.0', 8080)
server = loop.run_until_complete(server_coro)

print('Listening on 0.0.0.0:8080')

loop.add_signal_handler(signal.SIGTERM, loop.stop)

try:
    loop.run_forever()
finally:
    print('Terminating...')
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
