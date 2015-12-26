#!/usr/bin/env python
#! --encoding:utf-8--
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2012 Openstack, LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#!/usr/bin/env python

'''
Websocket proxy that is compatible with Openstack Nova.
Leverages websockify by Joel Martin
'''
from gevent import monkey
monkey.patch_all()

import socket
import sys
import struct
import time

import websockify

import xmlrpclib
from libvirt_vnc import get_vnc_port_by_uuid
import settings
from pprint import pprint

try:
    from urllib.parse import parse_qs, urlparse
except:
    from cgi import parse_qs
    from urlparse import urlparse


class WebSocketProxy(websockify.WebSocketProxy):
    def __init__(self, *args, **kwargs):
        websockify.WebSocketProxy.__init__(self, *args, **kwargs)

    def get_target(self, path):
        """
        @path: 从websocket客户端传递来的path参数
        ex: /websockify?host=192.2.3.44&uuid=cb7ecb5b-ec4a-c372-30d8-c11c686dc21f
        """
        args = parse_qs(urlparse(path)[4]) # 4 is the query from url

        if not args.has_key('host') or not len(args['host']):
            raise self.EClose("Host not present")
        
        if not args.has_key('uuid') or not len(args['uuid']):
            raise self.EClose("VM REF not present")

        host = args['host'][0].rstrip('\n')
        uuid = args['uuid'][0].rstrip('\n')
        
        port = get_vnc_port_by_uuid(host, uuid)
        
        return (host, port)

    def new_client(self):
        """
        Called after a new WebSocket connection has been established.
        """
        # 根据websocket client传递过来的PATH
        # 找到UUID对应的vnc location
        host, port = self.get_target(self.path)
        
        # 如果启用了录制VNC数据
        if self.record:
            vm_info_struct = "<64s128s64s128s"
            start_time = str(int(time.time()))
            client_address = attached_object.client_address[0] + ":" +str(attached_object.client_address[1])
            vm_info = struct.pack(vm_info_struct, host, vm_ref_id, start_time, client_address)
            
            fname = "%s_%s_%s.dat" % (host, vm_ref_id, start_time)
            self.msg("Server Recording to '%s'" % fname)
            
            # Send VMInfo to Recorder Server
            self.msg("Send VM info to Record server")
            try:
                record_server_ip = settings.VNC_RECORD_SERVER_IP
                record_server_port = settings.VNC_RECORD_SERVER_PORT
                record_sock = socket.create_connection((record_server_ip, record_server_port), 3)
                record_sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))
                rec_fd = record_sock.makefile()
                rec_fd.write(vm_info)
                rec_fd.flush()
                
                # Receive Reply from server
                self.msg("Receive Reply info from Record server")
                vm_info_reply_struct = "<i"
                size = struct.calcsize(vm_info_reply_struct)
                data = rec_fd.read(size)
                reply = struct.unpack(vm_info_reply_struct, data)
            except Exception, e:
                self.msg("Send Error: %s" % e)
            else:
                if reply[0] == 0:
                    self.msg("Start Send VNC Data to Recorder server...")
                    attached_object.rec = rec_fd
                    encoding = "binary"
                else:
                    attached_object.rec = None
             
        # Connect to the target
        self.msg("connecting to: %s:%s" % (host, port))

        tsock = self.socket(host, port,connect=True)
        
        if self.verbose and not self.daemon:
            print(self.traffic_legend)

        # Start proxying
        try:
            self.do_proxy(tsock)
        except:
            if tsock:
                tsock.shutdown(socket.SHUT_RDWR)
                tsock.close()
                self.vmsg("%s:%s: Target closed" % (host, port))
            raise


def run_server():
    host = settings.LISTEN_HOST
    port = settings.LISTEN_PORT
    server = WebSocketProxy(listen_host=host, listen_port=port, verbose=True, record=False)
    server.start_server()


if __name__ == '__main__':
    run_server()
