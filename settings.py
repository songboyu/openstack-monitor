# coding: utf-8
SERVER_API_PORT = 1984

APPS = (
    # "infrastracture",
    "virtual",
    # "cloudform",
    # "utils",
    # "system"
)

# openstack配置
VERSION = '2'
USERNAME = 'admin'
PASSWORD = '123456'
PROJECT_ID = 'admin'
ADMIN_TOKEN = '47bc5eb069f8cbeb1ed9'
AUTH_URL = 'http://controller:35357/v2.0'

# # 数据库配置
# db_engine = 'mysql'
# db_server = '173.26.100.209'
# db_username = 'root'
# db_password = '123456'
# db_database = 'cloud_monitor'

# 数据库配置
db_engine = 'mysql'
db_server = '125.211.198.185'
db_username = 'bluetech'
db_password = 'No.9332'
db_database = 'cloud_monitor'

# NOVNC配置
NOVNC_SERVER_IP = "125.211.198.185"
NOVNC_SERVER_PORT = 19999

# VNC Playback Server
VNC_PLAYBACK_SERVER_IP = "125.211.198.185"
VNC_PLAYBACK_SERVER_PORT = 23456