import sys
import os
import signal
import logging


sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'vendor')))


from tornado import web
import tornado.ioloop

from zenlines import zenlines


class MainHandler(web.RequestHandler):
    def get(self):
        letter = self.get_query_argument('q', None)
        if not letter:
            self.set_status(400)
            self.write('Bad Request')
            return

        try:
            zenline = zenlines[letter]
        except KeyError:
            self.set_status(404)
            self.write('Not Found')
            return

        self.write(zenline)

    def set_etag_header(self):
        pass

    def check_etag_header(self):
        return False


app = web.Application([('/', MainHandler)])
app.listen(8080)

logging.getLogger('tornado.access').disabled = True


loop = tornado.ioloop.IOLoop.current()

def stop(signal, frame):
    loop.stop()


signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGINT, stop)

loop.start()
