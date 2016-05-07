# coding: utf-8
import threading
import os
import sys
import time,datetime
import logging
import hashlib  

from libvmi_monitor_settings import *
from log import getlogger
import web

logger = getlogger("CloudMonitor")

web.config.debug = False
db = web.database(dbn=db_engine, host=db_server, db=db_database, 
							   user=db_username, pw=db_password)

ret = db.select('cloud_vhost',what='uuid,name,profile', where="`windows`=0")
profiles = {}
for line in ret:
    profiles[line['uuid']] = (line['name'], line['profile'])

def getHash(f):  
    line=f.readline()  
    hash=hashlib.md5()  
    while(line):  
        hash.update(line)  
        line=f.readline()  
    return hash.hexdigest() 
     
def IsHashEqual(f1,f2):  
    str1=getHash(f1)  
    str2=getHash(f2)  
    return str1==str2 

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
        (name, profile) = profiles[self.uuid]
        cmd = 'python vol.py -l vmi://%s --profile=%s linux_find_file -F "%s"' % (name, profile, self.path)
        res = os.popen(cmd).read()
        # logger.debug(res)
        inode = res[109:127]
        while True:
            ctime = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime())
            filename = self.path.split('/')[-1]
            filename = '%s_%s_%s' % (self.uuid, ctime, filename)

            cmd = 'python vol.py -l vmi://%s --profile=%s linux_find_file -i %s -O files/%s' % (name, profile, inode, filename)
            os.popen(cmd)

            cmd = 'ls -l files/%s' % filename
            res = os.popen(cmd).read()

            c = res.split()
            access = c[0]
            size = c[4]
            ret = db.select(table, where="`uuid`='%s' and `path`='%s' order by time desc" % (self.uuid, self.path))

            if len(ret) == 0:
                db.insert(table,uuid = self.uuid,
                                path = self.path,
                                size = size,
                                access=access,
                                time = ctime,
                                filename=filename
                                )
            else:
                f_old = open('files/'+list(ret)[0]['filename'],'rb')
                f_new = open('files/%s' % filename,'rb')
                if not IsHashEqual(f_old, f_new):
                    db.insert(table,uuid = self.uuid,
                                    path = self.path,
                                    size = size,
                                    access=access,
                                    time = ctime,
                                    filename=filename
                                    )
                else:
                    cmd = 'rm -rf files/%s' % filename
                    res = os.popen(cmd).read()
            logger.debug(ctime+" "+self.uuid+" "+self.path)

def main():
    logger.debug("============[OK] server start up!=============")

    threads = []
    # print profiles
    for (uuid,(name,profile)) in profiles.items():
        ret = db.select('file_monitor_list',what='uuid,path', where="`uuid`='%s'" % uuid)
        # t = command(k, 'linux_psaux')
        for line in ret:
            t = linux_file_change(uuid, line['path'])
            threads.append(t)
            logger.debug(uuid+" "+line['path'])

    for t in threads:
        t.setDaemon(True)
        t.start()

    for t in threads:
        t.join()

if __name__ == '__main__':    
    main()
