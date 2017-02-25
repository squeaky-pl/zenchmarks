import sys
import os.path

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'vendor')))


from aiohttp import web
import asyncio

from zenlines import zenlines


loop = asyncio.get_event_loop()


async def simple(request):
    try:
        letter = request.url.query['q']
    except KeyError:
        raise web.HTTPBadRequest()

    try:
        zenline = zenlines[letter]
    except KeyError:
        raise web.HTTPNotFound()

    return web.Response(text=zenline)


app = web.Application(loop=loop)
app.router.add_route('GET', '/', simple)

web.run_app(app, port=8080, access_log=None)
