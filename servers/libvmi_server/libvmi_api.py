# coding: utf-8
import sys
import os
import json
import time
import web
from libvmi_monitor_settings import *

from gevent import monkey
monkey.patch_all()
from gevent.wsgi import WSGIServer

web.config.debug = True

db = web.database(dbn=db_engine, host=db_server, db=db_database,
                               user=db_username, pw=db_password)
ret = db.select('cloud_vhost',what='uuid,profile')

profiles = {}
for line in ret:
    profiles[line['uuid']] = line['profile']

class Command(object):
    def GET(self, uuid, command):
        print uuid,command
        web.header('Access-Control-Allow-Origin','*')
        profile = profiles[uuid]

        cmd = 'python vol.py -f images/%s.dd --profile=%s %s' % (uuid, profile, command)
        res = os.popen(cmd).read()
        return res

class FileDownload(object):
    def GET(self,filename):
        BUF_SIZE = 262144
        try:
            f = open('files/'+filename, "rb")
            web.header('Content-Type','application/octet-stream')
            web.header('Content-disposition', 'attachment; filename=%s' % filename)
            while True:
                c = f.read(BUF_SIZE)
                if c:
                    yield c
                else:
                    break
        except Exception, e:
            print e
            yield 'Error'
        finally:
            if f:
                f.close()

if __name__ == '__main__':
    urls = (
        '/command/(.*)/(.*)','Command',
        '/filedownload/(.*)','FileDownload',
    )
    try:
        application = web.application(urls, globals()).wsgifunc()
        WSGIServer(('', api_server_port), application).serve_forever()

    except KeyboardInterrupt:
        pass
