# coding: utf-8
from settings import *
# import web

# db = web.database(dbn=db_engine,host=db_server,db=db_database,user=db_username,pw=db_password)

def get_all_vms_info_libvirt(db):
    vms_info = []
    table = "cloud_vhost"

    # ret = db.select(table,what='id,uuid,name,host,enable')
    sql = "select * from %s" % (table,)
    ret = db.query(sql)

    for line in ret:
        vms_info.append(dict(line))
    return vms_info

def get_all_hosts_info_libvirt(db):
    hosts_info = []
    table = "cloud_config"

    # ret = db.select(table,what='value',where="`key`='host'")
    sql = "select * from %s where `key`='host'" % (table,)
    print sql
    ret = db.query(sql)
    for line in ret:
        hosts_info.append(dict(line))
    return hosts_info

def get_file_monitor_list(uuid, db):
    files = []
    table = "file_monitor_list"

    # ret = db.select(table,what='id,uuid,name,host,enable')
    sql = "select * from %s where `uuid`='%s'" % (table,uuid)
    ret = db.query(sql)

    for line in ret:
        files.append(dict(line))
    return files

if __name__ == '__main__':
    print get_all_vms_info_libvirt()