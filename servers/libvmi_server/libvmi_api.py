# coding: utf-8
import sys
import os
import json
import time
import web

import pyvmi
from gevent import monkey
monkey.patch_all()
from gevent.wsgi import WSGIServer

from libvmi_monitor_settings import *

web.config.debug = True
db = web.database(dbn=db_engine, host=db_server, db=db_database,
                               user=db_username, pw=db_password)
ret = db.select('cloud_vhost',what='uuid,name,windows,profile')
profiles = {}

for line in ret:
    profiles[line['uuid']] = (line['windows'], line['name'], line['profile'])

def get_processes(vmi, win):
    # print win
    if win == 1:
        tasks_offset = vmi.get_offset("win_tasks")
        name_offset = vmi.get_offset("win_pname") - tasks_offset
        pid_offset = vmi.get_offset("win_pid") - tasks_offset
        list_head = vmi.read_addr_ksym("PsInitialSystemProcess")
    else:
        tasks_offset = vmi.get_offset("linux_tasks")
        name_offset = vmi.get_offset("linux_name") - tasks_offset
        pid_offset = vmi.get_offset("linux_pid") - tasks_offset
        list_head = vmi.translate_ksym2v("init_task")

    next_process = vmi.read_addr_va(list_head + tasks_offset, 0)
    list_head = next_process

    while True:
        procname = vmi.read_str_va(next_process + name_offset, 0)
        pid = vmi.read_32_va(next_process + pid_offset, 0)
        next_process = vmi.read_addr_va(next_process, 0)

        if (pid < 1<<16):
            yield pid, procname
        if (list_head == next_process):
            break

class Command_realtime_image(object):
    def GET(self, uuid, command):
        print uuid,command
        web.header('Access-Control-Allow-Origin','*')
        (win, name, profile) = profiles[uuid]

        cmd = 'python vol.py -f images/%s.dd --profile=%s %s' % (uuid, profile, command)
        res = os.popen(cmd).read()
            
        res = command+'\n\n'+res
        return res

class Command_realtime_vmi(object):
    def GET(self, uuid, command):
        print uuid,command
        web.header('Access-Control-Allow-Origin','*')
        (win, name, profile) = profiles[uuid]
        if command == 'libvmi_pslist':
            vmi = pyvmi.init(name, "complete")
            pslist = get_processes(vmi, win)
            res = ''
            for pid, procname in pslist:
                res += "[%5d] %s" % (pid, procname)+'\n'
            res = command+'\n\n'+res
            return res
        else:
            cmd = 'python vol.py -l vmi://%s --profile=%s %s' % (name, profile, command)
            res = os.popen(cmd).read()
            res = command+'\n\n'+res
            return res

class Command_not_realtime(object):
    def GET(self, uuid, command):
        print uuid,command
        web.header('Access-Control-Allow-Origin','*')
        (win, name, profile) = profiles[uuid]

        res = ''
        ret = db.select('vol_history',what='uuid,command,value,time', where="`uuid`='%s' and `command`='%s'" % (uuid,command))
        if len(ret) > 0:
            line = ret[0]
            res = str(line['time']) +'\n\n' + line['value']

        res = command+'\n\n'+res
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

class RegistryDownload(object):
    def GET(self,uuid,filename):
        BUF_SIZE = 262144
        try:
            f = open('registry/%s/%s' % (uuid,filename), "rb")
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
        '/command/not_realtime/(.*)/(.*)','Command_not_realtime',
        '/command/realtime/vmi/(.*)/(.*)','Command_realtime_vmi',
        '/command/realtime/image/(.*)/(.*)','Command_realtime_image',
        '/filedownload/(.*)','FileDownload',
        '/registrydownload/(.*)/(.*)','RegistryDownload',
    )
    try:
        application = web.application(urls, globals()).wsgifunc()
        WSGIServer(('', api_server_port), application).serve_forever()

    except KeyboardInterrupt:
        pass
