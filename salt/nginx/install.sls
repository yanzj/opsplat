servers_dir:
  cmd.run:  
    - names:  
      - mkdir -p /export/servers
      - chown AAAAA.AAAAA /export/servers
    - unless: test -d /export/servers
log_dir:
  cmd.run:  
    - names:  
      - mkdir -p /export/log/nginx
      - chown AAAAA.AAAAA /export/log/
    - unless: test -d /export/log/nginx
  
nginx_source:  
  file.managed:  
    - name: /export/package/nginx-1.14.0.tar.gz
    - unless: test -e /export/package/nginx-1.14.0.tar.gz
    - user: root  
    - group: root  
    - makedirs: True  
    - source: salt://nginx/file/nginx-1.14.0.tar.gz
nginx_extract:  
  cmd.run:  
    - cwd: /export/package/  
    - names:   
      - tar zxf nginx-1.14.0.tar.gz
    - unless: test -d /export/package/nginx-1.14.0 
    - require:  
      - file: nginx_source  
nginx_pkg:  
  pkg.installed:  
    - pkgs:  
      - gcc  
      - gcc-c++  
      - openssl-devel  
      - pcre-devel  
      - pcre 
      - zlib   
      - openssl
      - zlib-devel  
nginx_compile:  
  cmd.run:  
    - cwd: /export/package/nginx-1.14.0
    - names:  
      - ./configure --user=nobody --group=nobody --prefix=/export/servers/nginx --with-http_stub_status_module --with-http_gzip_static_module --with-http_ssl_module --with-http_realip_module  
      - make  
      - make install  
    - require:  
      - cmd: nginx_extract  
      - cmd: servers_dir 
      - cmd: log_dir  
      - pkg: nginx_pkg  
    - unless: test -d /export/servers/nginx  
create_dir:  
  cmd.run:  
    - names:  
      - mkdir -p /export/servers/nginx/conf/vhost
    - unless: test -d /export/servers/nginx/conf/vhost  
    - require:   
      - cmd: nginx_compile  
createlog_dir:  
  cmd.run:  
    - names:  
      - mkdir -p /export/log/nginx
    - unless: test -d /export/log/nginx
    - require:   
      - cmd: nginx_compile  
