# coding: utf-8
from views import *

url_handlers = [
    (r"^/$", Cloud_VMs_Libvirt_Handler),
    # 虚拟机详细信息（图表）
    (r"/virtual/vms/(.*)/gragh", Cloud_VM_Data_Handler),
    # 列出所有虚拟机信息
    # (r"/virtual/vms$", Cloud_VMs_Nova_Handler),
    (r"/virtual/vms", Cloud_VMs_Libvirt_Handler),
    # 列出所有主机信息
    # (r"/virtual/hosts$", Cloud_Hosts_Nova_Handler),
    (r"/virtual/hosts", Cloud_Hosts_Libvirt_Handler),
    # 回放虚拟机控制台
    # (r"/virtual/vms/(.*)/console/playback$", Cloud_VM_Console_Playback_Nova_Handler),
    (r"/virtual/vms/(.*)/console/playback", Cloud_VM_Console_Playback_Libvirt_Handler),
    # 回放虚拟机控制台
    # (r"/virtual/vms/(.*)/console/record", Cloud_VM_Console_Record_Nova_Handler),
    (r"/virtual/vms/(.*)/console/record", Cloud_VM_Console_Record_Libvirt_Handler),
    # 连接虚拟机控制台
    # (r"/virtual/vms/(.*)/console$", Cloud_VM_Console_Nova_Handler),
    (r"/virtual/vms/(.*)/console", Cloud_VM_Console_Libvirt_Handler),
    # libvmi详情
    (r"/virtual/vms/(.*)/vmi", Cloud_VM_VMI_Handler),
    # 文件变化
    (r"/virtual/vms/(.*)/file_change", Cloud_VM_File_Change_Handler),
    # vm list of one xenserver
    # the arguments are: ip address of xenserver
    #(r"/virtual/xenserver/(.*)/virtual", XenServer_VMs_Handler),
    # charts of one vm
    # the arguments are: host/uuid/chart type
    # (r"^/virtual/xenserver/hosts/$", XenServer_Get_ALL),
    # (r"^/virtual/xenserver/hosts/([^/]+)/$", XenServer_Get_Host),
    # (r"^/virtual/xenserver/([^/]+)/virtual/$", XenServer_Get_ALL_vms),
    # (r"^/virtual/xenserver/([^/]+)/virtual/([^/]+)/console/$", XenServer_Get_VM_Console),
    # (r"^/virtual/xenserver/([^/]+)/virtual/([^/]+)/console/playback/$", XenServer_VM_Console_Playback),
    # (r"^/virtual/xenserver/([^/]+)/virtual/([^/]+)/perfmon/$", XenServer_VM_Perfmon),
    # (r"^/virtual/xenserver/([^/]+)/([^/]+)/chart/([^/]+)/$", XenServer_VMs_Chart_Handler),

    #(r"/virtual/libvirt", Libvirt_Handler),
]