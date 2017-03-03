import sys
import os.path


sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'vendor')))


from sanic import Sanic
from sanic.response import text
from sanic.exceptions import InvalidUsage, NotFound
from sanic.response import text

from zenlines import zenlines

app = Sanic(__name__)


@app.route("/")
async def hello(request):
    try:
        letter = request.args['q'][0]
    except KeyError:
        raise InvalidUsage()

    try:
        zenline = zenlines[letter]
    except KeyError:
        raise NotFound()

    return text(zenline)


app.run(host="0.0.0.0", port=8080)
