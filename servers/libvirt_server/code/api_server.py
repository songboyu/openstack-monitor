# coding: utf-8
import sys
try:
    from gevent import monkey
    monkey.patch_all()
    from gevent.wsgi import WSGIServer
    import gevent
except (ImportError,ImportWarning) as e:
    print "Can not find python-gevent, in ubuntu just run \"sudo apt-get install python-gevent\"."
    print e
    sys.exit(1)

import os
import json
import time
import mimerender
from cloud_monitor_settings import *

try:
    import web
except (ImportError,ImportWarning) as e:
    print "Can not find python-webpy, in ubuntu just run \"sudo apt-get install python-webpy\"."
    print e
    sys.exit(1)

mimerender = mimerender.WebPyMimeRender()
web.config.debug = True

db = web.database(dbn=db_engine,host=db_server,db=db_database,user=db_username,pw=db_password)

render_xml = lambda message: '<message>%s</message>'%message
render_json = lambda **args: json.dumps(args)
render_html = lambda message: '<html><body>%s</body></html>'%message
render_txt = lambda message: message

class getInstanceList(object):
    @mimerender(
        default = 'json',
        html = render_html,
        xml  = render_xml,
        json = render_json,
        txt  = render_txt
    )
    def GET(self):
        web.header('Access-Control-Allow-Origin','*')
        table = 'cloud_vhost'
        try:
            results = list()
            ret = db.select(table,what='id,uuid,host,enable')
            for line in ret:
                results.append(dict(line))
        except Exception,e:
            raise web.internalerror(message=e)
        return {'message':results}

class setIntervalCheck():
    @mimerender(
        default = 'json',
        html = render_html,
        xml  = render_xml,
        json = render_json,
        txt  = render_txt
    )
    def POST(self):
        web.header('Access-Control-Allow-Origin','*')
        table='cloud_config'
        data = web.input()
        try:
            interval = data.interval
        except AttributeError:
            return {'message':'attribute_error'}
        if int(interval)<=0:
            return {'message':'failed, interval too short'}
        elif int(interval)>=3600: 
            return {'message':'failed, interval too long'}
        db.update(table,where="`key`='interval_check'",value=interval)
        return {'message':'success, new check interval is '+interval}

class setIntervalTravelsal():
    @mimerender(
        default = 'json',
        html = render_html,
        xml  = render_xml,
        json = render_json,
        txt  = render_txt
    )
    def POST(self):
        web.header('Access-Control-Allow-Origin','*')
        table='cloud_config'
        data = web.input()
        try:
            interval = data.interval
        except AttributeError:
            return {'message':'attribute_error'}
        if int(interval)<=0:
            return {'message':'failed, interval too short'}
        elif int(interval)>=3600: 
            return {'message':'failed, interval too long'}
        db.update(table,where="`key`='interval_travelsal'",value=interval)
        return {'message':'success, new travelsal interval is '+interval}

class enableByUUID():
    @mimerender(
        default='json',
        html = render_html,
        xml = render_xml,
        json = render_json,
        txt = render_txt
    )
    def POST(self, uuid):
        web.header('Access-Control-Allow-Origin','*')
        import datetime
        table = 'cloud_vhost'
        data = web.input()
        try:
            enable = data.enable
        except AttributeError:
            return {'message':'attribute_error'}
        try:
            db.update(table,where="`uuid`='%s'" % uuid,enable=int(enable))
            return {'message':'success'}
        except Exception,e:
            raise web.notfound(message=e) 

class addHost():
    @mimerender(
        default='json',
        html = render_html,
        xml = render_xml,
        json = render_json,
        txt = render_txt
    )
    def POST(self, uuid):
        web.header('Access-Control-Allow-Origin','*')
        import datetime
        table = 'cloud_config'
        data = web.input()
        try:
            host = data.host
        except AttributeError:
            return {'message':'attribute_error'}
        try:
            db.insert(table, host=host)
            return {'message':'success'}
        except Exception,e:
            raise web.notfound(message=e) 

class deleteHost():
    @mimerender(
        default='json',
        html = render_html,
        xml = render_xml,
        json = render_json,
        txt = render_txt
    )
    def DELETE(self, host):
        web.header('Access-Control-Allow-Origin','*')
        import datetime
        table = 'cloud_config'
        try:
            db.delete(table,where="`key`='host' and `value`='%s' " % host)
            return {'message':'success'}
        except Exception,e:
            raise web.notfound(message=e)  

class getDataByUUID():
    @mimerender(
        default='json',
        html = render_html,
        xml = render_xml,
        json = render_json,
        txt = render_txt
    )
    def POST(self, uuid):
        web.header('Access-Control-Allow-Origin','*')
        table = 'cloud_result'
        data = web.input()
        try:
            stime = data.stime
            etime = data.etime
        except AttributeError:
            return {'message':'attribute_error'}
        try:
            ret = db.select(table,where="`time`>='%s' and `time`<='%s' and `uuid`='%s'" % (stime,etime,uuid))
            results = list()
            for line in ret:
                results.append(dict(line))
        except Exception,e:
            raise web.internalerror(message=e)
        return {'message':results}
    def DELETE(self, host):
        web.header('Access-Control-Allow-Origin','*')
        import datetime
        table = 'cloud_vhost'
        try:
            db.delete(table,where="`uuid`='%s'" % uuid)
            return {'message':'success'}
        except Exception,e:
            raise web.notfound(message=e)    

if __name__ == '__main__':

    urls = (
        # 列出所有虚拟机
        '/instances','getInstanceList',
        # 设置是否抓取指定uuid的instance
        '/enable/(.*)','enableByUUID',
        # 按时间起始结束，获取指定uuid的instance数据/删除指定虚拟机
        '/instances/(.*)','getDataByUUID',

        # 设置抓取数据间隔（秒）
        '/interval/check','setIntervalCheck',
        # 设置获取虚拟机列表间隔（秒）
        '/interval/travelsal','setIntervalTravelsal',

        # 添加物理机IP
        '/host/add','addHost',
        # 删除物理机IP
        '/host/(.*)','deleteHost',
    )
    try:
        application = web.application(urls, globals()).wsgifunc()
        WSGIServer(('', api_server_port), application).serve_forever()

    except KeyboardInterrupt:
        pass
    
    
