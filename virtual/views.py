# coding: utf-8
import re
import json
from datetime import datetime

import torndb
from tornado import gen
from tornado.httpclient import AsyncHTTPClient

from common.api.NovaAPI import *
from common.api.LibvirtAPI import *
from common.init import *
from settings import *

db = torndb.Connection(db_server, db_database, db_username, db_password)

class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)

class Cloud_VM_File_Change_Handler(WiseHandler):
    def get(self,uuid):
        host = self.get_argument("host", None, strip=True)
        name = self.get_argument("name", None, strip=True)
        files = get_file_monitor_list(uuid,db)
        self.render("virtual/vm_file_change.html", uuid=uuid, host=host, name=name, files=files)

    def post(self, uuid):
        table = 'file_change_history'
        try:
            path = self.get_argument("path", None, strip=True)
        except AttributeError:
            self.write({'message': 'attribute_error'})
        try:
            sql = "select * from %s where `uuid`='%s' and `path`='%s'" % (table, uuid, path)
            results = db.query(sql)
            results = {'message': results}
            # results = list()
            # for line in ret:
            #     results.append(dict(line))
        except Exception, e:
            self.send_error(500)
            self.write(e)
        self.write(json.dumps(results, cls=CJsonEncoder))

class Cloud_VM_VMI_Handler(WiseHandler):
    def get(self,uuid):
        host = self.get_argument("host", None, strip=True)
        print host
        windows = self.get_argument("windows", None, strip=True)
        self.render("virtual/vm_vmi.html", uuid=uuid, host=host, windows=windows)

class Cloud_VMs_Nova_Handler(WiseHandler):
    def get(self):
        vms = get_all_vms_info_nova()
        self.render("virtual/vms_list_nova.html", vms=vms)

class Cloud_VMs_Libvirt_Handler(WiseHandler):
    def get(self):
        vms = get_all_vms_info_libvirt(db)
        self.render("virtual/vms_list_libvirt.html", vms=vms)

class Cloud_Hosts_Nova_Handler(WiseHandler):
    def get(self):
        hosts = get_all_hosts_info_nova()
        self.render("virtual/hosts_list_nova.html", hosts=hosts)

class Cloud_Hosts_Libvirt_Handler(WiseHandler):
    def get(self):
        hosts = get_all_hosts_info_libvirt(db)
        self.render("virtual/hosts_list_libvirt.html", hosts=hosts)

class Cloud_VM_Data_Handler(WiseHandler):
    def get(self, uuid):
        self.render("virtual/vm_graph.html", uuid=uuid)

    def post(self, uuid):
        table = 'cloud_result_in_row'
        try:
            stime = self.get_argument("stime", None, strip=True)
            etime = self.get_argument("etime", None, strip=True)
        except AttributeError:
            self.write({'message': 'attribute_error'})
        try:
            sql = "select * from %s where time>='%s' and time<='%s' and uuid='%s'" % (table, stime, etime, uuid)
            results = db.query(sql)
            results = {'message': results}
            # results = list()
            # for line in ret:
            #     results.append(dict(line))
        except Exception, e:
            self.send_error(500)
            self.write(e)
        self.write(json.dumps(results))

class Cloud_VM_Console_Nova_Handler(WiseHandler):
    def get(self, uuid):
        vm = get_vm_info_by_uuid(uuid)

        self.render("virtual/vm_console_nova.html",
                    novnc_host=NOVNC_SERVER_IP,
                    novnc_port=NOVNC_SERVER_PORT,
                    vm=vm)

class Cloud_VM_Console_Record_Nova_Handler(WiseHandler):
    def get(self, uuid):
        vm = get_vm_info_by_uuid(uuid)

        self.render("virtual/vm_console_record_nova.html",
                    novnc_host=NOVNC_SERVER_IP,
                    novnc_port=NOVNC_SERVER_PORT,
                    vm=vm)

class Cloud_VM_Console_Playback_Nova_Handler(WiseHandler):
    @gen.coroutine
    @web.asynchronous
    def get(self, uuid):
        vm = get_vm_info_by_uuid(uuid)
        host = vm.to_dict()['OS-EXT-SRV-ATTR:host']
        playback_server_ip = VNC_PLAYBACK_SERVER_IP
        playback_server_port = str(VNC_PLAYBACK_SERVER_PORT)
        playback_server = playback_server_ip + ":" + playback_server_port

        def on_fetch(response):
            try:
                result = json.loads(response.body)
                files = result['data']
                self.render("virtual/vm_console_playback_nova.html",
                            files=files, host_address=host,
                            vm=vm, status=0, playback_server=playback_server)
            except Exception, e:
                self.render("virtual/vm_console_playback_nova.html",
                            files=None, host_address=host,
                            vm=vm, status=2, playback_server=None)

        http_client = AsyncHTTPClient()
        query = "?host=%s&vm_uuid=%s" % (host, uuid)
        url = "http://%s/serv/listfile" % playback_server + query
        http_client.fetch(url, callback=on_fetch)

class Cloud_VM_Console_Libvirt_Handler(WiseHandler):
    def get(self, uuid):
        host = self.get_argument("host", None, strip=True)

        self.render("virtual/vm_console_libvirt.html",
                    novnc_host=NOVNC_SERVER_IP,
                    novnc_port=NOVNC_SERVER_PORT,
                    host=host,
                    uuid=uuid)

class Cloud_VM_Console_Record_Libvirt_Handler(WiseHandler):
    def get(self, uuid):
        host = self.get_argument("host", None, strip=True)

        self.render("virtual/vm_console_record_libvirt.html",
                    novnc_host=NOVNC_SERVER_IP,
                    novnc_port=NOVNC_SERVER_PORT,
                    host=host,
                    uuid=uuid)

class Cloud_VM_Console_Playback_Libvirt_Handler(WiseHandler):
    @gen.coroutine
    @web.asynchronous
    def get(self, uuid):
        host = self.get_argument("host", None, strip=True)

        playback_server_ip = VNC_PLAYBACK_SERVER_IP
        playback_server_port = str(VNC_PLAYBACK_SERVER_PORT)
        playback_server = playback_server_ip + ":" + playback_server_port

        def on_fetch(response):
            try:
                result = json.loads(response.body)
                files = result['data']
                self.render("virtual/vm_console_playback_libvirt.html",
                            files=files, host_address=host,
                            uuid=uuid, status=0, playback_server=playback_server)
            except Exception, e:
                self.render("virtual/vm_console_playback_libvirt.html",
                            files=None, host_address=host,
                            uuid=uuid, status=2, playback_server=None)

        http_client = AsyncHTTPClient()
        query = "?host=%s&vm_uuid=%s" % (host, uuid)
        url = "http://%s/serv/listfile" % playback_server + query
        http_client.fetch(url, callback=on_fetch)
