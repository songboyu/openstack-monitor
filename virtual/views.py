# coding: utf-8
import re
import json

import torndb
from tornado import gen
from tornado.httpclient import AsyncHTTPClient

from common.api.NovaAPI import *
from common.init import *
from settings import *

db = torndb.Connection(db_server, db_database, db_username, db_password)

class Cloud_VMs_Handler(WiseHandler):
    def get(self):
        vms = get_all_vms_info()
        self.render("virtual/vms_list.html", vms=vms)

class Cloud_Hosts_Handler(WiseHandler):
    def get(self):
        hosts = get_all_hosts_info()
        self.render("virtual/hosts_list.html", hosts=hosts)

class Cloud_VM_Data_Handler(WiseHandler):
    def get(self, uuid):
        vm = get_vm_info_by_uuid(uuid)
        self.render("virtual/vm_graph.html", uuid=uuid, vm=vm)

    def post(self, uuid):
        table = 'cloud_result'
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

class Cloud_VM_Console_Handler(WiseHandler):
    def get(self, uuid):
        vm = get_vm_info_by_uuid(uuid)

        self.render("virtual/vm_console.html",
                    novnc_host=NOVNC_SERVER_IP,
                    novnc_port=NOVNC_SERVER_PORT,
                    vm=vm)

class Cloud_VM_Console_Record_Handler(WiseHandler):
    def get(self, uuid):
        vm = get_vm_info_by_uuid(uuid)

        self.render("virtual/vm_console_record.html",
                    novnc_host=NOVNC_SERVER_IP,
                    novnc_port=NOVNC_SERVER_PORT,
                    vm=vm)

class Cloud_VM_Console_Playback_Handler(WiseHandler):
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
                self.render("virtual/vm_console_playback.html",
                            files=files, host_address=host,
                            vm=vm, status=0, playback_server=playback_server)
            except Exception, e:
                self.render("virtual/vm_console_playback.html",
                            files=None, host_address=host,
                            vm=vm, status=2, playback_server=None)

        http_client = AsyncHTTPClient()
        query = "?host=%s&vm_uuid=%s" % (host, uuid)
        url = "http://%s/serv/listfile" % playback_server + query
        http_client.fetch(url, callback=on_fetch)
