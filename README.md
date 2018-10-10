简介：<br>
   封装jenkins在运维平台打包、立项、申请上线、审批、执行发布、回滚、等功能,平台小而精。<br>


安装使用要求：<br>
1、python2.7   django1.11 、pip install python-jenkins mysql-python <br>
2、创建数据库python manage.py makemigrations ljapps && python manage.py migrate，创建超级用户 <br>
2、数据库初始化项目tomcat   dubbo  daemon  项目类型Apptype表<br>
3、初始化端口类型表Porttype 为http  tomcat_shutdown  tcp  3种类型<br>
4、立项前创建对应的项目组group表<br>
5、创建jenkins的template模板（重要）(git_template    与svn_template ljapps/views.py的confjks 需要使用),jenkins 2.46.3版本配置jenkins打包后第一次需要在jenkins打包，平台无法发现刚创建的项目，最高版本的jenkins不存在此问题，但是不支持1.7的jdk打包 <br>
6、配置jenkins的账号密码与url <br>
7、配置jenkins的运行用户无密码访问svn与git <br>
8、立项工单添加访问权限(暂时未做) <br>
9、配置setting的fix7script    fix8script   tomcat7  tomcat8 <br>
10、配置jenkins日志级别javax.jmdns	OFF（根据需求设置,解决jenkins磁盘空间占满的问题） <br>
11、立项脚本中curl的api地址配置配置, jenkins打包后jks.sh脚本的api地址配置 <br>
12、配置idc为阿里云（根据自己真实情况设置） <br>
13、salt的agent的/etc/sudoers的Defaults    requiretty，修改为 #Defaults    requiretty，表示不需要控制终端。 <br>
14、系统内机器IP与应用、负载均衡相关ip等均使用内网IP地址，保持和salt的授信节点ip相同，如不相同部署应用是salt执行命令会找不到对应主机 <br>
15、nginx的负载均衡文件/export/servers/nginx/conf/vhost/nginx_backend.conf，配置切流量功能的tomcat的后端upstream必须存放在此文件中。<br>
16、必须严格保证/export及次级目录的权限与、salt部署脚本中用户权限相同 <br>
说明，运维平台的构建与部署是一个复杂的事情，各个人的思路不一样，部署很麻烦，任何一个公司的运维平台都这样，后面想再搭建一个都懒得动，有想部署此平台玩玩的朋友，直接加我qq696317，联系我，你找好机器，我直接语音帮助部署起来，但是项目可能好久没碰，自己也不太熟悉了，见谅。

立项页面
![image](https://github.com/renxiaotian/opsplat/blob/master/ljops/static/tupian/lixiang.jpg)

打包页面
![image](https://github.com/renxiaotian/opsplat/blob/master/ljops/static/tupian/dabao.jpg)

申请发布
![image](https://github.com/renxiaotian/opsplat/blob/master/ljops/static/tupian/shenqingfabu.jpg)

执行发布
![image](https://github.com/renxiaotian/opsplat/blob/master/ljops/static/tupian/fabu.jpg)

查看项目
![image](https://github.com/renxiaotian/opsplat/blob/master/ljops/static/tupian/chakanproject.jpg)
