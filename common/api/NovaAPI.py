# coding: utf-8
from novaclient import client
from settings import *

nova = client.Client(VERSION, USERNAME, PASSWORD, PROJECT_ID, AUTH_URL)

def get_all_vms_info_nova():
    vms_info = []
    for server in nova.servers.list():
        dict = server.to_dict()
        dict['networks'] = server.networks
        dict['created'] = dict['created'].replace('T',' ').replace('Z',' ')
        vms_info.append(dict)
    return vms_info

def get_all_hosts_info_nova():
    hosts_info = []
    for host in nova.hosts.list():
        dict = host.to_dict()
        hosts_info.append(dict)
    return hosts_info

def get_vm_info_by_uuid_nova(uuid):
    server = nova.servers.find(id=uuid)
    return server

if __name__ == '__main__':
    print get_all_vms_info()