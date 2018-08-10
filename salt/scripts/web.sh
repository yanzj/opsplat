#!/bin/bash
#update stop start restart delete jstat jstack taillog
MKDIR='/bin/mkdir'
#URL_PKG_BASE='https://#################'
#WGET='/usr/bin/wget --http-user=AAAAA --http-password=1qaz@WSX --no-check-certificate'
WGET="$WGET --tries=1 --no-verbose"
DATE='/bin/date'
#RUNUSER='AAAAA'
ECHO='/bin/echo'
TIMEOUT='/usr/bin/timeout'
timestamp() {
$DATE +'%Y-%m-%d %H:%M:%S'
}

debug (){
ts=`timestamp`
$ECHO "$ts DEBUG: $@"
}

check_jdk() {
 echo "$1"
 [[ "$1" =~ "jdk1.7" ]] && jdk=jdk1.7
 [[ "$1" =~ "jdk1.8" ]] && jdk=jdk1.8
 cd $REPOS_DIR
 if [ ! -e "/export/package/$1" ] 
   then
    if [  -e "/export/local/$jdk" -o -L "/export/local/$jdk" ] 
     then
       echo "$jdk aaaaa"
       echo "/export/local/$jdk is error"
       exit 1
     else
        echo "$WGET -q --timeout=300  $URL_PKG_BASE/zipbck/$1.zip"
         $WGET -q --timeout=300  $URL_PKG_BASE/zipbck/$1.zip
       chown $RUNUSER $1.zip
        mv $1.zip /export/package/
       chown $RUNUSER.$RUNUSER /export/package/$1.zip
       cd /export/package/
       sudo -u $RUNUSER unzip -q $1.zip
    sudo -u $RUNUSER   ln -s  /export/package/$1  /export/local/$jdk
       echo "wget jdk and ln -s  /export/package/$1  /export/local/$jdk"
       cd $REPOS_DIR
   fi
 else
   if  [  -e "/export/local/$jdk" -a -L "/export/local/$jdk" ]
    then
     echo "jdk is ok"
    else
     echo "/export/local/$jdk  is ERROR"
     exit 1
   fi
 fi
}

check_catalina_home() {
 cd $REPOS_DIR
 if [ ! -e "/export/local/$1" ] 
   then
        echo "$WGET -q --timeout=300  $URL_PKG_BASE/zipbck/$1.zip"
         $WGET -q --timeout=300  $URL_PKG_BASE/zipbck/$1.zip
       [ ! -e $1.zip ] && exit 1
       chown $RUNUSER $1.zip
        mv $1.zip /export/local
       chown $RUNUSER.$RUNUSER /export/local/$1.zip
       cd /export/local/
       sudo -u $RUNUSER unzip -q $1.zip
       cd $REPOS_DIR
 else
     echo "catalina_home is ok"
 fi
}

check_tomcat() {
 cd $REPOS_DIR
 if [ ! -e "/export/package/$2" ] 
   then
       cd /export/package/
        $WGET -q --timeout=300  $URL_PKG_BASE/zipbck/$2.zip
       chown $RUNUSER $2.zip
      sudo -u $RUNUSER unzip -q $2.zip
    if [ ! -e "/export/server/$1" -o -L "/export/server/$1" ] 
     then
      echo "##########"
    else
    sudo -u $RUNUSER  ln -s  /export/package/$2  /export/server/$1
    fi
    cd $REPOS_DIR
 else
    echo "tomcat dir  is ok"
 fi
 [ ! -e /export/log/$1 ] &&  sudo -u $RUNUSER mkdir /export/log/$1
}
check_app() {
 cd $REPOS_DIR
 if [ ! -e "/export/content/$2" ] 
   then
       echo "$2 is not exsit"
        $WGET -q --timeout=300  $URL_PKG_BASE/$2.zip
       chown $RUNUSER.$RUNUSER $2.zip
        unzip -q  $2.zip
        chown -R $RUNUSER.$RUNUSER $2
        rm -rf $2.zip
        mv $2 /export/content/
       cd $REPOS_DIR
 else
    echo "content $2 is exsit"
 fi
}
mklinks(){
sudo -u $RUNUSER ln -s /export/package/$3   /export/server/$1
sudo -u $RUNUSER ln -s /export/content/$2   /export/www/$1

}
delinks(){
rm -f /export/server/$1 
rm -f /export/www/$1 
}

start_up(){
sudo -u $RUNUSER /export/server/$1/bin/start.sh
}

stop_down(){
sudo -u $RUNUSER /export/server/$1/bin/stop.sh

}
re_start(){
stop_down
start_up
}

update() {
echo '$1:'$1
echo '$2:'$2
echo '$3:'$3
echo '$4:'$4
echo '$5:'$5
echo "update tomcat app "
echo "$1 is tomcat app"
echo "$1 update dest version $3"
[ -e "/export" ] ||  $MKDIR -p /export && chown $RUNUSER.$RUNUSER /export
REPOS_DIR='/tmp/packages'
[ -e "$REPOS_DIR" ] || sudo -u $RUNUSER $MKDIR -p $REPOS_DIR
REPOS_APP_DIR='/export/package'
[ -e "$REPOS_APP_DIR" ] ||  sudo -u $RUNUSER $MKDIR -p $REPOS_APP_DIR
REPOS_WEB_DIR='/export/content'
[ -e "$REPOS_WEB_DIR" ] || sudo -u $RUNUSER $MKDIR -p $REPOS_WEB_DIR
APP_DIR='/export/local'
[ -e "$APP_DIR" ] || sudo -u $RUNUSER $MKDIR -p $APP_DIR
WY_SERVER_DIR='/export/server'
[ -e "$WY_SERVER_DIR" ] || sudo -u $RUNUSER $MKDIR -p $WY_SERVER_DIR
APP_TOMCAT_DIR='/export/server'
[ -e "$APP_TOMCAT_DIR" ] || sudo -u $RUNUSER $MKDIR -p $APP_TOMCAT_DIR
APP_RESIN_DIR='/export/server'
[ -e "$APP_RESIN_DIR" ] || sudo -u $RUNUSER $MKDIR -p $APP_RESIN_DIR
SERVERS_DIR='/export/servers'
[ -e "$SERVERS_DIR" ] || sudo -u $RUNUSER $MKDIR -p $SERVERS_DIR
WEB_DIR='/export/www'
[ -e "$WEB_DIR" ] || sudo -u $RUNUSER $MKDIR -p $WEB_DIR
GLOBAL_LOG_DIR='/export/log'
[ -e "$GLOBAL_LOG_DIR" ] || sudo -u $RUNUSER $MKDIR -p $GLOBAL_LOG_DIR
DATA_DIR='/export/data'
[ -e "$DATA_DIR" ] || sudo -u $RUNUSER $MKDIR -p $DATA_DIR

#check_jdk jdk1.7.0_51
check_jdk $4
#check_catalina_home tomcat-7.0.69
check_catalina_home $5
check_tomcat $1 $2
check_app  $1  $3
stop_down $1
sleep 15
delinks $1  $3 $2
mklinks $1 $3 $2
start_up $1
}


restart() {
echo "update tomcat app "
#curl 
echo "$1 is tomcat app, jdk is 1.7 ,tomcat7"
# error exit 1
echo "$1 update dest version $2"
}


case $1 in
update)
update $2 $3 $4 $5 $6
;;
restart)
restart $2 $3 
;;
*)
echo "error"
;;
esac
