#coding: utf-8
import libvirt

class getNodeValue(object):
    def __init__(self, xml_file_or_string, nodes):
        import xml.dom.minidom
        self.nodes = nodes
        try:
            fd = open(xml_file_or_string)
            self.doc = xml.dom.minidom.parse(xml_file_or_string)
        except:
            self.doc = xml.dom.minidom.parseString(xml_file_or_string)
        else:
            fd.close()
        
    def get_value(self):
        node = self.nodes.split('.')
        num_of_disk = 0
        num_of_interface = 0
        vir_disks = []
        vir_interfaces = []
        if node[0]:
            node0 = self.doc.getElementsByTagName(node[0])[0]
        if node[1]:
            node1 = node0.getElementsByTagName(node[1])[0]
        for child in node1.childNodes:
            if child.nodeName == "disk":
                num_of_disk +=1
            if child.nodeName == "interface":
                num_of_interface +=1
        if node[2] and node[2]=="disk":
            for i in range(num_of_disk):
                node2 = node1.getElementsByTagName(node[2])[i]
                for n in node2.childNodes:
                    if n.nodeName == node[3]:
                        vir_disks.append(n.getAttribute(node[4]))
            return vir_disks
        if node[2] and node[2]=="interface":
            for i in range(num_of_interface):
                node2 = node1.getElementsByTagName(node[2])[i]
                for n in node2.childNodes:
                    if n.nodeName == node[3]:
                        vir_interfaces.append(n.getAttribute(node[4]))
            return vir_interfaces

if __name__ == '__main__':
	UUID = '6cea7be6-600f-4545-a1a7-b8c9f2a70550'
	conn = libvirt.open('qemu+ssh://173.26.100.211/system')
	dom = conn.lookupByUUIDString(UUID)
	print 'UUID: '+dom.UUIDString()
	print dom.info()
	domain_xml = dom.XMLDesc(0)

	vir_disks = getNodeValue(domain_xml, 'domain.devices.disk.target.dev').get_value()
	for disk in vir_disks:
		print u'硬盘信息: '+disk
		print dom.blockInfo(disk, 0)
		print dom.blockStats(disk)

	vir_interfaces = getNodeValue(domain_xml, 'domain.devices.interface.target.dev').get_value()
	for interface in vir_interfaces:
		print u'网卡信息: '+interface
        print dom.interfaceStats(interface)