# A simple HTTP server implemented using h11 and Curio
# Adapted from: https://github.com/njsmith/h11/blob/master/examples/curio-server.py


import urllib.parse
from itertools import count
from socket import SHUT_WR
from wsgiref.handlers import format_date_time
import sys
import os


sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'vendor')))


import curio
import h11

MAX_RECV = 2 ** 16
TIMEOUT = 10

from zenlines import zenlines

################################################################
# I/O adapter: h11 <-> curio
################################################################

# The core of this could be factored out to be usable for curio-based clients
# too, as well as servers. But as a simplified pedagogical example we don't
# attempt this here.
class CurioHTTPWrapper:
    _next_id = count()

    def __init__(self, sock):
        self.sock = sock
        self.conn = h11.Connection(h11.SERVER)
        # Our Server: header
        self.ident = " ".join([
            "h11-example-curio-server/{}".format(h11.__version__),
            h11.PRODUCT_ID,
        ]).encode("ascii")
        # A unique id for this connection, to include in debugging output
        # (useful for understanding what's going on if there are multiple
        # simultaneous clients).
        self._obj_id = next(CurioHTTPWrapper._next_id)

    async def send(self, event):
        # The code below doesn't send ConnectionClosed, so we don't bother
        # handling it here either -- it would require that we do something
        # appropriate when 'data' is None.
        assert type(event) is not h11.ConnectionClosed
        data = self.conn.send(event)
        await self.sock.sendall(data)

    async def _read_from_peer(self):
        if self.conn.they_are_waiting_for_100_continue:
            go_ahead = h11.InformationalResponse(
                status_code=100,
                headers=self.basic_headers())
            await self.send(go_ahead)
        try:
            data = await self.sock.recv(MAX_RECV)
        except ConnectionError:
            # They've stopped listening. Not much we can do about it here.
            data = b""
        self.conn.receive_data(data)

    async def next_event(self):
        while True:
            event = self.conn.next_event()
            if event is h11.NEED_DATA:
                await self._read_from_peer()
                continue
            return event

    async def shutdown_and_clean_up(self):
        # When this method is called, it's because we definitely want to kill
        # this connection, either as a clean shutdown or because of some kind
        # of error or loss-of-sync bug, and we no longer care if that violates
        # the protocol or not. So we ignore the state of self.conn, and just
        # go ahead and do the shutdown on the socket directly. (If you're
        # implementing a client you might prefer to send ConnectionClosed()
        # and let it raise an exception if that violates the protocol.)
        #
        # Curio bug: doesn't expose shutdown()
        with self.sock.blocking() as real_sock:
            try:
                real_sock.shutdown(SHUT_WR)
            except OSError:
                # They're already gone, nothing to do
                return
        # Wait and read for a bit to give them a chance to see that we closed
        # things, but eventually give up and just close the socket.
        # XX FIXME: possibly we should set SO_LINGER to 0 here, so
        # that in the case where the client has ignored our shutdown and
        # declined to initiate the close themselves, we do a violent shutdown
        # (RST) and avoid the TIME_WAIT?
        # it looks like nginx never does this for keepalive timeouts, and only
        # does it for regular timeouts (slow clients I guess?) if explicitly
        # enabled ("Default: reset_timedout_connection off")
        async with curio.ignore_after(TIMEOUT):
            try:
                while True:
                    # Attempt to read until EOF
                    got = await self.sock.recv(MAX_RECV)
                    if not got:
                        break
            finally:
                await self.sock.close()

    def basic_headers(self):
        # HTTP requires these headers in all responses (client would do
        # something different here)
        return [
            ("Date", format_date_time(None).encode("ascii")),
            ("Server", self.ident),
        ]

################################################################
# Server main loop
################################################################
async def http_serve(sock, addr):
    wrapper = CurioHTTPWrapper(sock)
    while True:
        assert wrapper.conn.states == {
            h11.CLIENT: h11.IDLE, h11.SERVER: h11.IDLE}

        try:
            async with curio.timeout_after(TIMEOUT):
                event = await wrapper.next_event()
                if type(event) is h11.Request:
                    await send_echo_response(wrapper, event)
        except Exception as exc:
            await maybe_send_error_response(wrapper, exc)

        if wrapper.conn.our_state is h11.MUST_CLOSE:
            await wrapper.shutdown_and_clean_up()
            return
        else:
            try:
                wrapper.conn.start_next_cycle()
            except h11.ProtocolError:
                states = wrapper.conn.states
                await maybe_send_error_response(
                    wrapper,
                    RuntimeError("unexpected state {}".format(states)))
                await wrapper.shutdown_and_clean_up()
                return

################################################################
# Actual response handlers
################################################################

# Helper function
async def send_simple_response(wrapper, status_code, content_type, body):
    headers = wrapper.basic_headers()
    headers.append(("Content-Type", content_type))
    headers.append(("Content-Length", str(len(body))))
    res = h11.Response(status_code=status_code, headers=headers)
    await wrapper.send(res)
    await wrapper.send(h11.Data(data=body))
    await wrapper.send(h11.EndOfMessage())

async def maybe_send_error_response(wrapper, exc):
    # If we can't send an error, oh well, nothing to be done
    if wrapper.conn.our_state not in {h11.IDLE, h11.SEND_RESPONSE}:
        return
    try:
        if isinstance(exc, h11.RemoteProtocolError):
            status_code = exc.error_status_hint
        else:
            status_code = 500
        body = str(exc).encode("utf-8")
        await send_simple_response(wrapper,
                                   status_code,
                                   "text/plain; charset=utf-8",
                                   body)
    except Exception as exc:
        pass


async def send_echo_response(wrapper, request):
    url = urllib.parse.urlparse(request.target)
    query = urllib.parse.parse_qs(url.query)

    if url.path != b"/":
        await send_simple_response(wrapper,
                                   404,
                                   "text/plain; charset=utf-8",
                                   b"Not Found")
        return

    if request.method != b"GET":
        await send_simple_response(wrapper,
                                   405,
                                   "text/plain; charset=utf-8",
                                   b"Method Not Allowed")
        return

    while True:
        event = await wrapper.next_event()
        if type(event) is h11.EndOfMessage:
            break
        assert type(event) is h11.Data

    try:
        letter = query[b'q'][0].decode('utf-8')
    except KeyError:
        await send_simple_response(wrapper,
                                   400,
                                   "text/plain; charset=utf-8",
                                   b"Bad Request")

        return

    try:
        zenline = zenlines[letter]
    except KeyError:
        await send_simple_response(wrapper,
                                   404,
                                   "text/plain; charset=utf-8",
                                   b"Not Found")
        return

    await send_simple_response(wrapper,
                               200,
                               "text/plain; charset=utf-8",
                               zenline.encode('utf-8'))

################################################################
# Run the server
################################################################

if __name__ == "__main__":
    kernel = curio.Kernel()
    print("Listening on http://localhost:8080")
    kernel.run(curio.tcp_server("localhost", 8080, http_serve))
