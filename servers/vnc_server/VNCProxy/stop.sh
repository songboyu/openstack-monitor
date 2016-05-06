ps -ef|grep vnc_proxy_server|grep -v grep|cut -c 9-15|xargs kill -9
