# coding: utf-8
import threading
import Queue
import os
import sys
import time,datetime
import logging
import xml
import argparse

from cloud_monitor_settings import *
from monitor import ThreadPoolMonitor
from log import getlogger
import web as _web
import libvirt as _libvirt

logger = getlogger("CloudMonitor")

_web.config.debug = False

try:
	db = _web.database(dbn=db_engine, host=db_server, db=db_database, 
									user=db_username, pw=db_password)
except Exception, e:
	logger.exception(e)
	raise e

cloud_vhost_table = 'cloud_vhost'
cloud_config_table = 'cloud_config'
cloud_result_table = 'cloud_result_in_row'

interval_check_peroid = 0
interval_travelsal_libvirtd = 0
current_time = datetime.datetime.now()

queue_host_list = Queue.Queue()  #put hostlist here
queue_result = Queue.Queue()    #put result of check here
queue_log = Queue.Queue()       #put log message here

#make current process to daemon
def daemonize (stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    # Do first fork.
    try: 
        pid = os.fork() 
        if pid > 0:
            sys.exit(0)   # Exit first parent.
    except OSError, e: 
        sys.stderr.write ("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror) )
        sys.exit(1)

    # Decouple from parent environment.
    os.chdir("/") 
    os.umask(0) 
    os.setsid() 

    # Do second fork.
    try: 
        pid = os.fork() 
        if pid > 0:
            sys.exit(0)   # Exit second parent.
    except OSError, e: 
        sys.stderr.write ("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror) )
        sys.exit(1)

    # Now I am a daemon!
    
    # Redirect standard file descriptors.
    si = open(stdin, 'r')
    so = open(stdout, 'a+')
    se = open(stderr, 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

#libvirt client: actually do some work
def multi_host_libvirt_check(host_dict):
    for host in host_dict:
        try:
            conn = _libvirt.open('qemu+ssh://%s/system' % host)
        except Exception, e:
            logger.exception(e)

        time_sleep = 2

        result = {}

        stats = conn.getAllDomainStats()
        for s in stats:
            dom = s[0]
            stat = s[1]

            uuid = dom.UUIDString()
            info = dom.info()

            if info[0] != 1:
                logger.debug("non-exists uuid: %s" % uuid)
                db.delete(cloud_vhost_table, where="`uuid`='%s'" % uuid)
                continue

            result[uuid] = {}
            result[uuid]['cpu_time'] = dom.info()[4]

            result[uuid]['block_rd_reqs']   = stat['block.0.rd.reqs']
            result[uuid]['block_rd_bytes']  = stat['block.0.rd.bytes']
            result[uuid]['block_wr_reqs']   = stat['block.0.wr.reqs']
            result[uuid]['block_wr_bytes']  = stat['block.0.wr.bytes']
            result[uuid]['block_fl_reqs']   = stat['block.0.fl.reqs']
            
            result[uuid]['net_rx_bytes']    = stat['net.0.rx.bytes']
            result[uuid]['net_rx_packets']  = stat['net.0.rx.pkts']
            result[uuid]['net_rx_errs']     = stat['net.0.rx.errs']
            result[uuid]['net_rx_drop']     = stat['net.0.rx.drop']
            result[uuid]['net_tx_bytes']    = stat['net.0.tx.bytes']
            result[uuid]['net_tx_packets']  = stat['net.0.tx.pkts']
            result[uuid]['net_tx_errs']     = stat['net.0.tx.errs']
            result[uuid]['net_tx_drop']     = stat['net.0.tx.drop']

        # sleep
        start_time = time.time()
        time.sleep(time_sleep)
        end_time = time.time()  
        time_passed = end_time - start_time

        stats = conn.getAllDomainStats()
        for s in stats:
            dom = s[0]
            stat = s[1]

            uuid = dom.UUIDString()
            info = dom.info()

            if info[0] != 1:
                continue

            result[uuid]['uuid']    = uuid
            result[uuid]['name']    = dom.name()
            result[uuid]['host']    = host
            result[uuid]['time']    = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            result[uuid]['state']   = info[0]
            result[uuid]['max_memory']      = info[1]
            result[uuid]['memory_usage']    = info[2]
            result[uuid]['number_cpus']     = info[3]
            result[uuid]['cpu_usage']       = 0

            cputime_passd = info[4] - result[uuid]['cpu_time']
            cpu_usage = "%.3f" % (float(100 * cputime_passd) / float(time_passed * result[uuid]['number_cpus'] * 1000000000))
            
            result[uuid]['cpu_usage'] = cpu_usage
            
            result[uuid]['block_capacity']    = stat['block.0.capacity']
            result[uuid]['block_allocation']  = stat['block.0.allocation']
            result[uuid]['block_physical']    = stat['block.0.physical']

            result[uuid]['block_rd_reqs']   = (stat['block.0.rd.reqs']  - result[uuid]['block_rd_reqs'])  /time_passed
            result[uuid]['block_rd_bytes']  = (stat['block.0.rd.bytes'] - result[uuid]['block_rd_bytes']) /time_passed
            result[uuid]['block_wr_reqs']   = (stat['block.0.wr.reqs']  - result[uuid]['block_wr_reqs'])  /time_passed
            result[uuid]['block_wr_bytes']  = (stat['block.0.wr.bytes'] - result[uuid]['block_wr_bytes']) /time_passed
            result[uuid]['block_fl_reqs']   = (stat['block.0.fl.reqs']  - result[uuid]['block_fl_reqs'])  /time_passed
            
            result[uuid]['net_rx_bytes']    = (stat['net.0.rx.bytes']   - result[uuid]['net_rx_bytes'])   /time_passed
            result[uuid]['net_rx_packets']  = (stat['net.0.rx.pkts']    - result[uuid]['net_rx_packets']) /time_passed
            result[uuid]['net_rx_errs']     = (stat['net.0.rx.errs']    - result[uuid]['net_rx_errs'])    /time_passed
            result[uuid]['net_rx_drop']     = (stat['net.0.rx.drop']    - result[uuid]['net_rx_drop'])    /time_passed
            result[uuid]['net_tx_bytes']    = (stat['net.0.tx.bytes']   - result[uuid]['net_tx_bytes'])   /time_passed
            result[uuid]['net_tx_packets']  = (stat['net.0.tx.pkts']    - result[uuid]['net_tx_packets']) /time_passed
            result[uuid]['net_tx_errs']     = (stat['net.0.tx.errs']    - result[uuid]['net_tx_errs'])    /time_passed
            result[uuid]['net_tx_drop']     = (stat['net.0.tx.drop']    - result[uuid]['net_tx_drop'])    /time_passed
            
            del result[uuid]['cpu_time']
            
            logger.debug('OK '+result[uuid]['time']+' '+dom.UUIDString())
            queue_result.put(result[uuid])

        conn.close()

#read uuids from remote libvirtd and store them to database
class thread_read_host_list(threading.Thread):
    def __init__(self):
        super(thread_read_host_list, self).__init__()
        self.daemon = False
        
    def run(self):
        while True:
            host_list = db.select(cloud_config_table, 
                                  where="`key`='host'").list()
            #interval that travelsal uuids from remote libvirtd
            interval_travelsal_libvirtd = int(db.select(cloud_config_table, 
                                          where="`key`='interval_travelsal'").list()[0]['value'])
            for host in host_list:
                host = host['value']
                try:
                    dom_ids = []
                    uri = 'qemu+ssh://%s/system' % host
                    try:
                       conn = _libvirt.open(uri)
                    except Exception, e:
                        logger.exception(e)
                        break
                    domain_ids = conn.listDomainsID()
                    for domain_id in domain_ids:
                        dom = conn.lookupByID(domain_id)
                        uuid = dom.UUIDString()
                        name = dom.name()
                        db_result = db.select(cloud_vhost_table, where="uuid='%s'" % uuid)
                        if not db_result.list():
                            db.insert(cloud_vhost_table, uuid=uuid, host=host, name=name, enable=1)
                except Exception, e:
                    logger.exception(e)
                time.sleep(interval_travelsal_libvirtd)

#read host list from db (table cloud_vhost)
class thread_get_host_list_from_db(threading.Thread):
    def __init__(self):
        super(thread_get_host_list_from_db, self).__init__()
        self.daemon = False

    def run(self):
        while True:
            try:
                #interval that used to check instance
                interval_check_peroid = int(db.select(cloud_config_table, 
                                              where="`key`='interval_check'").list()[0]['value'])
                lists = db.select(cloud_vhost_table).list()
                host_dict = {}
                for line in lists:
                    if int(line['enable']) == 1:
                        if line['host'] in host_dict:
                            host_dict[line['host']].append(line['uuid'])
                        else:
                            host_dict[line['host']] = []
                            host_dict[line['host']].append(line['uuid'])

                queue_host_list.put(host_dict) 
            except Exception, e:
                logger.exception(e)

            time.sleep(interval_check_peroid)

# checker thread
class thread_do_check(threading.Thread):
    def __init__(self):
        super(thread_do_check, self).__init__()
        self.daemon = False

    def run(self):
        while True:
            try:
                host_dict = queue_host_list.get(True)
                multi_host_libvirt_check(host_dict)
            except Exception, e:
                logger.exception(e)
                raise e

#store result to database
class thread_update_db(threading.Thread):
    def __init__(self):
        super(thread_update_db, self).__init__()
        self.daemon = False

    def run(self):
        while True:
            try:
                result = queue_result.get(True)
                db.insert(cloud_result_table, **result)
            except Exception, e:
                logger.exception(e)

def main():
    parser = argparse.ArgumentParser(description="cloud monitor cli argparser")
    exclusive_group = parser.add_mutually_exclusive_group(required=False)
    
    logger.debug("[OK] server start up!")
    daemon_log_path = os.getcwd()+"/log/daemon.log"
    daemonize('/dev/null', daemon_log_path, daemon_log_path)

    pool_do_check = []
    pool_update_db = []
    num_of_do_check = 10
    num_of_update_db = 3

    tr_pool = []
    for i in range(1):
        tr = thread_read_host_list()
        tr_pool.append(tr)

    for i in tr_pool:
        i.start()
        tg = thread_get_host_list_from_db()
        tg.start()
    
    for i in range(num_of_do_check):
        td = thread_do_check()
        pool_do_check.append(td)
    
    for t in pool_do_check:
        t.start()
    
    for i in range(num_of_update_db):
        tu = thread_update_db()
        pool_update_db.append(tu)
    
    for t in pool_update_db: 
        t.start()

    monitor = ThreadPoolMonitor(tr=(tr_pool, ), \
            td=(pool_do_check, ), \
            tu=(pool_update_db, ))
    monitor.start()

if __name__ == '__main__':    
    main()


