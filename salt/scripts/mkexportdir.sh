#!/bin/bash
MKDIR='/bin/mkdir'
RUNUSER='admin'

[ -e "/export" ] ||  $MKDIR -p /export && chown $RUNUSER.$RUNUSER /export
chown $RUNUSER.$RUNUSER /export
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

