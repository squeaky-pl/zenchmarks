import sys
import os.path

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'vendor')))

import falcon


class ZenResource(object):
    def on_get(self, req, resp):
        # marker = req.get_param('marker') or ''
        # limit = req.get_param_as_int('limit') or 50
        #
        # try:
        #     result = self.db.get_things(marker, limit)
        # except Exception as ex:
        #     self.logger.error(ex)
        #
        #     description = ('Aliens have attacked our base! We will '
        #                    'be back as soon as we fight them off. '
        #                    'We appreciate your patience.')
        #
        #     raise falcon.HTTPServiceUnavailable(
        #         'Service Outage',
        #         description,
        #         30)

        # An alternative way of doing DRY serialization would be to
        # create a custom class that inherits from falcon.Request. This
        # class could, for example, have an additional 'doc' property
        # that would serialize to JSON under the covers.
        resp.body = 'Hello'
        resp.set_header('Connection', 'Keep-Alive')
        resp.content_type = 'text/plain; charset=utf-8'
        resp.status = falcon.HTTP_200


app = falcon.API()
zen = ZenResource()
app.add_route('/', zen)
