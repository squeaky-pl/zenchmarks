import asyncio
import sys
import os.path

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'vendor')))


from aiohttp import web, WSMsgType


loop = asyncio.get_event_loop()


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
                ws.send_str(msg.data + '/answer')
        elif msg.type == WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())

    return ws


app = web.Application(loop=loop)
app.router.add_route('GET', '/', websocket_handler)

web.run_app(app, port=8080, access_log=None)
