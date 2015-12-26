# coding: utf-8
from xml.etree import ElementTree as ET
import libvirt

def get_vnc_port_by_uuid(host, uuid):
	conn = libvirt.open('qemu+ssh://root@%s/system' % host)

	domain = conn.lookupByUUIDString(uuid)

	#get the XML description of the VM
	domXml = domain.XMLDesc(0)
	root = ET.fromstring(domXml)

	#get the VNC port
	graphics = root.find('./devices/graphics')
	port = graphics.get('port')

	return port

if __name__ == '__main__':
	print get_vnc_port_by_uuid('125.211.198.186', 'ed590096-26cf-4a35-9984-8897f9d77fd8')