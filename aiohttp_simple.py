import sys
import os.path
import random
import string

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'vendor')))


from aiohttp import web
import asyncio
#import uvloop


#loop = uvloop.new_event_loop()
#asyncio.set_event_loop(loop)
loop = asyncio.get_event_loop()


zen = """
Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated.
Flat is better than nested.
Sparse is better than dense.
Readability counts.
Special cases aren't special enough to break the rules.
Although practicality beats purity.
Errors should never pass silently.
Unless explicitly silenced.
In the face of ambiguity, refuse the temptation to guess.
There should be one-- and preferably only one --obvious way to do it.
Although that way may not be obvious at first unless you're Dutch.
Now is better than never.
Although never is often better than *right* now.
If the implementation is hard to explain, it's a bad idea.
If the implementation is easy to explain, it may be a good idea.
Namespaces are one honking great idea -- let's do more of those!
""".strip().splitlines()


zens = dict(zip(
    random.choices(string.ascii_letters, k=37),
    random.choices(zen, k=19) + random.choices(zen, k=18)))


async def simple(request):
    try:
        letter = request.url.query['q']
    except KeyError:
        raise web.HTTPBadRequest()

    try:
        zenline = zens[letter]
    except KeyError:
        raise web.HTTPNotFound()

    return web.Response(text=zenline)


app = web.Application(loop=loop)
app.router.add_route('GET', '/', simple)

web.run_app(app, port=8080, access_log=None)
