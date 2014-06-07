#!/usr/bin/env python

import BaseHTTPServer
import os
import sys
import time

HOST_NAME = ''
PORT_NUMBER = 8000
VARS = ('FLOOP', 'BRUP', 'GORP')

def log(format, *args):
    sys.stderr.write('%s: %s\n' % (time.asctime(), format % args))
    sys.stderr.flush()

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        log(format, *args)

    def do_GET(s):
        """Respond to a GET request."""
        s.send_response(200)
        s.send_header("Content-type", "text/plain")
        s.end_headers()
        s.wfile.write("The server is now up! THIS IS VERSION 2.\n")
        for k in VARS:
            s.wfile.write("%s is %s\n" % (k, os.environ.get(k)))
        s.wfile.write("You accessed path: %s\n" % s.path)

if __name__ == '__main__':
    try:
        sys.stderr = open(sys.argv[1], 'a')
    except IndexError:
        pass

    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    log('Server starts - %s:%s', HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    log('Server stops - %s:%s', HOST_NAME, PORT_NUMBER)
    sys.stderr.close()
