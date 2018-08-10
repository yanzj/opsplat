include:  
  - nginx.install  
  
{% set nginx_user = 'nobody' %}  
  
nginx_conf:  
  file.managed:  
    - name: /export/servers/nginx/conf/nginx.conf  
    - source: salt://nginx/file/nginx.conf  
    - template: jinja  
    - defaults:  
      nginx_user: {{ nginx_user }}  
      num_cpus: {{ grains['num_cpus'] }}  
nginx_log_cut:               
  file.managed:  
    - name: /export/servers/nginx/sbin/nginx_log_cut.sh  
    - source: salt://nginx/file/nginx_log_cut.sh  
  cron.present:      
    - name: sh /export/servers/nginx/sbin/nginx_log_cut.sh  
    - user: root  
    - minute: 1
    - hour: 0  
    - require:  
      - file: nginx_log_cut  
