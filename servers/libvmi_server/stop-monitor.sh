ps -ef|grep libvmi_monitor_server|grep -v grep|cut -c 9-15|xargs kill -9