import sys
import os.path

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'vendor')))

import falcon

from zenlines import zenlines


class ZenResource(object):
    def on_get(self, req, resp):
        q = req.get_param('q')

        resp.content_type = 'text/plain; charset=utf-8'

        if not q:
            resp.body = 'Bad Request'
            resp.status = falcon.HTTP_400
            return

        try:
            zenline = zenlines[q]
        except KeyError:
            resp.body = 'Not Found'
            resp.status = falcon.HTTP_404
            return

        resp.body = zenline
        resp.status = falcon.HTTP_200


app = falcon.API()
zen = ZenResource()
app.add_route('/', zen)

if __name__ == '__main__':
    os.system('PYTHONPATH=vendor {} -m gunicorn.app.wsgiapp -b 127.0.0.1:8080 zenhttp_falcon:app'.format(sys.executable))
