# coding: utf-8
import threading
import os
import sys
import time,datetime
import logging

from libvmi_monitor_settings import *
from log import getlogger
import web

logger = getlogger("CloudMonitor")

web.config.debug = False
db = web.database(dbn=db_engine, host=db_server, db=db_database, 
							   user=db_username, pw=db_password)

ret = db.select('cloud_vhost',what='uuid,profile', where="`windows`=0")
profiles = {}
for line in ret:
    profiles[line['uuid']] = line['profile']

class command(threading.Thread):
    def __init__(self, uuid, command):
        super(command, self).__init__()
        self.daemon = True
        self.uuid = uuid
        self.command = command
        
    def run(self):
        table = 'vol_history'
        while True:
            profile = profiles[self.uuid]
            cmd = 'python vol.py -f images/%s.dd --profile=%s %s' % (self.uuid, profile, self.command)
            res = os.popen(cmd).read()
            # logger.debug(res)

            ctime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            ret = db.select(table, where="`uuid`='%s' and `command`='%s'" % (self.uuid, self.command))
            if len(ret) == 0:
                db.insert(table,uuid = self.uuid,
                                    command = self.command,
                                    value = res,
                                    time = ctime)
            else:
                db.update(table, where="`uuid`='%s' and `command`='%s'" % (self.uuid, self.command),
                                    value = res,
                                    time = ctime)
            logger.debug(ctime+" "+self.uuid+" "+self.command)

class linux_file_change(threading.Thread):
    def __init__(self, uuid, path):
        super(linux_file_change, self).__init__()
        self.daemon = True
        self.uuid = uuid
        self.path = path

    def run(self):
        table = 'file_change_history'
        while True:
            profile = profiles[self.uuid]
            cmd = 'python vol.py -f images/%s.dd --profile=%s linux_find_file -F "%s"' % (self.uuid, profile, self.path)
            res = os.popen(cmd).read()
            # logger.debug(res)
            inode = res[109:127]
            ctime = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime())
            filename = self.path.split('/')[-1]
            cmd = 'python vol.py -f images/%s.dd --profile=%s linux_find_file -i %s -O files/%s_%s_%s' % (self.uuid, profile, inode, self.uuid, ctime, filename)
            res = os.popen(cmd).read()

            cmd = 'ls -l files/%s_%s_%s' % (self.uuid, ctime, filename)
            res = os.popen(cmd).read()

            c = res.split()
            access = c[0]
            size = c[4]
            ret = db.select(table, where="`uuid`='%s' and `path`='%s' order by time desc" % (self.uuid, self.path))

            if len(ret) == 0 or size != list(ret)[0]['size']:
                db.insert(table,uuid = self.uuid,
                                    path = self.path,
                                    size = size,
                                    access=access,
                                    time = ctime,
                                    filename="%s_%s_%s" % (self.uuid, ctime, filename)
                                    )
            else:
                cmd = 'rm -rf files/%s_%s_%s' % (self.uuid, ctime, filename)
                res = os.popen(cmd).read()
            logger.debug(ctime+" "+self.uuid+" "+self.path)

def main():
    logger.debug("============[OK] server start up!=============")

    threads = []
    # print profiles
    for (uuid,profile) in profiles.items():
        ret = db.select('file_monitor_list',what='uuid,path', where="`uuid`='%s'" % uuid)
        # t = command(k, 'linux_psaux')
        for line in ret:
            t = linux_file_change(uuid, line['path'])
            threads.append(t)
            print uuid,line['path']

    for t in threads:
        t.setDaemon(True)
        t.start()
        t.join()

if __name__ == '__main__':    
    main()
