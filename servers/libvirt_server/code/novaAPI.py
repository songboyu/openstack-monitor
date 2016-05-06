# coding: utf-8
from novaclient import client
from cloud_monitor_settings import *
import json

def print_server(server):
    print("-"*35)
    print("id: %s" % server.id)
    print("name: %s" % server.name)
    print("image: %s" % server.image)
    print("flavor: %s" % server.flavor)
    print("key name: %s" % server.key_name)
    print("user_id: %s" % server.user_id)
    print("status: %s" % server.status)
    print("networks: %s" % server.networks)
    print("hostId: %s" % server.hostId)
    print("addresses: %s" % server.addresses)
    print("to_dict: %s" % server.to_dict())
    # print("novnc_url: %s" % server.get_vnc_console('novnc'))
    print 

if __name__ == '__main__':
	nova = client.Client(VERSION, USERNAME, PASSWORD, PROJECT_ID, AUTH_URL)
	# for server in nova.servers.list():
	# 	print
	# 	print server
	# 	print json.dumps(server.to_dict())
	for host in nova.hosts.list():
		print
		print host.to_dict()
