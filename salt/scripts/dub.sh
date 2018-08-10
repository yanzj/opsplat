#!/bin/bash
#update stop start restart delete jstat jstack taillog
MKDIR='/bin/mkdir'
#URL_PKG_BASE='https://60.205:1000'
#WGET='/usr/bin/wget --http-user=AAAAA --http-password=1qaz@WSX --no-check-certificate'
WGET="$WGET --tries=1 --no-verbose"
DATE='/bin/date'
#RUNUSER='###'
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
 cd $REPOS_DIR
 [[ "$1" =~ "jdk1.7" ]] && jdk=jdk1.7
 [[ "$1" =~ "jdk1.8" ]] && jdk=jdk1.8
 if [ ! -e "/export/package/$1" ] 
   then
    if [  -e "/export/local/$jdk" -o -L "/export/local/$jdk" ] 
     then
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
sudo -u $RUNUSER ln -s /export/content/$2   /export/server/$1
}

delinks(){
rm -f /export/server/$1 
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
echo "update  app "
echo "$1 update dest version $2"
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
check_jdk  $3
check_app $1 $2
stop_down $1
sleep 10
delinks $1 $2
mklinks $1 $2
start_up $1
}




case $1 in
update)
update $2 $3 $4
;;
restart)
re_start $2 $3
;;
*)
echo "error"
;;
esac
