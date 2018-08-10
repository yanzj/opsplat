#!/bin/bash

sed  -i  "s@server.*$1:$2@#server $1:$2@g" /export/servers/nginx/conf/vhost/nginx_backend.conf
sleep 1
/export/servers/nginx/sbin/nginx -s reload
