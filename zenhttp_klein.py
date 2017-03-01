import sys
import os


sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'vendor')))


from twisted.web.http import NOT_FOUND, BAD_REQUEST

from klein import run, route

from zenlines import zenlines

@route("/", methods=["GET"])
def resource(request):
    letter = request.args.get("q", [None])[0]
    if not letter:
        request.setResponseCode(BAD_REQUEST)
        return "Bad Request"

    try:
        zenline = zenlines[letter]
    except KeyError:
        request.setResponseCode(NOT_FOUND)
        return "Not Found"

    return zenline

run("localhost", 8080, logFile=open(os.devnull, "w"))
