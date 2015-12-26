# -- coding: utf-8 --
import os
import sys
import signal
import time

from tornado import ioloop
from tornado.options import options

from common.init import *
from common.api.loader import load_url_handlers
from logger import logger


class iApplication(web.Application):
    def __init__(self):
        settings = {
            'static_path': os.path.join(os.path.dirname(__file__), "static"),
            'js': os.path.join(os.path.dirname(__file__), "js"),
            'css': os.path.join(os.path.dirname(__file__), "css"),
            'img': os.path.join(os.path.dirname(__file__), "img"),
            'template_path': os.path.join(os.path.dirname(__file__), "templates"),
        }
    
        handlers = [
            (r"^/$", MainHandler),
            (r"^/static/(.*)", web.StaticFileHandler, dict(path=settings['static_path'])),
            (r"^/css/(.*)", web.StaticFileHandler, dict(path=settings['css'])),
            (r"^/js/(.*)", web.StaticFileHandler, dict(path=settings['js'])),
            (r"^/img/(.*)", web.StaticFileHandler, dict(path=settings['img'])),
        ]
        
        apps = load_url_handlers()
        handlers.extend(apps)
        # custom http error handler
        handlers.append((r"/.*", PageNotFound))
        web.Application.__init__(self, handlers, **settings)

    def DELETE(self, host):
        web.header('Access-Control-Allow-Origin','*')
        import datetime
        table = 'cloud_vhost'
        try:
            db.delete(table,where="`uuid`='%s'" % uuid)
            return {'message':'success'}
        except Exception,e:
            raise web.notfound(message=e)


class MainHandler(WiseHandler):
    def get(self):
        self.render("index.html")

class Watcher:   
    def __init__(self):   
        self.child = os.fork()   
        if self.child == 0:   
            return  
        else:   
            self.watch()
            
    def watch(self):   
        try:   
            os.wait()   
        except (KeyboardInterrupt, SystemExit):   
            # I put the capital B in KeyBoardInterrupt so I can   
            # tell when the Watcher gets the SIGINT
            print "Server exit at %s." % time.ctime()
            self.kill()   
        sys.exit()   
  
    def kill(self):   
        try:   
            os.kill(self.child, signal.SIGKILL)   
        except OSError: pass 
    

if __name__ == '__main__':
    try:
        port = int(sys.argv[1])
    except Exception:
        port = 1984
    
    # Watcher()
    
    options.parse_command_line()
    
    app = iApplication()
    app.listen(port, xheaders=True)
    logger.info("Start server on %d OK." % port)
    
    try:
        ioloop = ioloop.IOLoop.instance()
        ioloop.start()
    except (KeyboardInterrupt, SystemExit):
        ioloop.close()

