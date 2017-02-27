import sys
import os.path
import urllib.parse
import signal

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'vendor')))


from gevent.pywsgi import WSGIServer

from zenlines import zenlines
import gevent.signal


def application(env, start_response):
    query = urllib.parse.parse_qs(env['QUERY_STRING'])

    if env['PATH_INFO'] != '/':
        start_response(
            '404 Not Found',
            [('Content-Type', 'text/plain; charset=utf-8')])
        return [b"Not Found"]

    if env['REQUEST_METHOD'] != 'GET':
        start_response(
            '405 Method Not Allowed',
            [('Content-Type', 'text/plain; charset=utf-8')])
        return [b'Method Not Allowed']

    try:
        letter = query['q'][0]
    except KeyError:
        start_response(
            '400 Bad Request',
            [('Content-Type', 'text/plain; charset=utf-8')])
        return [b'Bad Request']

    try:
        zenline = zenlines[letter]
    except KeyError:
        start_response(
            '404 Not Found',
            [('Content-Type', 'text/plain; charset=utf-8')])
        return [b'Not Found']

    start_response(
        '200 OK',
        [('Content-Type', 'text/plain; charset=utf-8')])
    return [zenline.encode('utf-8')]


server = WSGIServer(('127.0.0.1', 8080), application, log=None)


def stop_server(signal, frame):
    server.stop()


gevent.signal.signal(signal.SIGTERM, stop_server)
gevent.signal.signal(signal.SIGINT, stop_server)

server.serve_forever()
