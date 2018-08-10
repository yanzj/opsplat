#!/bin/sh
#The script creation time is 2018.02.05 
#By Xiaotian


DATE='/bin/date'

timestamp() {
    $DATE +'%Y-%m-%d %H:%M:%S'
}

die (){
    ts=`timestamp`
    echo "$ts  ERR: $@"
    exit 1
}

echo "============================="
echo "============================="
echo "==Now updating, ready......=="
echo "=====GO  GO  GO=============="


if [ $# -ne 6 ];then
    echo "Warning!!!!!!!"
    echo "The parameter must be 4, 1.Tomcat application name 2.Tomcat start port 3.Tomcat Stop port  4.Tomcat version 5.app id 6.urllocation."
    echo "example:  fix_tomcat7-jdk1.7.sh app-manager-web 8081 8082 tomcat-7.0.69  1 ."
    exit 1
    fi
app_name=$1
nowdate=`date +%Y%m%dT%H%M`
#datapm_path=/home/fjradmin/cgi-bin
#grep -q \'$app_name\' $datapm_path/Data.pm && die "该应用$app_name已经存在,请检查应用名称是否正确....." 
#需要确定项目是否存在,已经存在 die "该应用$app_name已经存在,请检查应用名称是否正确.....
cd /export/adminpkgs/
if [ ! -x "./zipbck" ]; then
    echo "The directory zipbck does not exist, Now create ....."
    mkdir './zipbck'
     fi
unzip ./tomcat7-template-version-jdk1.7.zip

echo "##########################"
echo "##########################"
if [ $# -eq 6 ];then
    newname=$1
    start_port=$2
    shut_port=$3
    tomcat_version=$4
    urllocation=$6
    sed  "/APP=/s/experss/$newname/g" ./tomcat7-template-version/bin/env.sh |grep APP=
    sed  "/CATALINA_HOME=/s/tomcat/$tomcat_version/g" ./tomcat7-template-version/bin/env.sh |grep CATALINA_HOME=
    sed  "/docBase=/s/experss/$newname/g" ./tomcat7-template-version/conf/server.xml |grep docBase=
    sed  "/protocol/s/7000/$start_port/g" ./tomcat7-template-version/conf/server.xml |grep protocol
    sed  "/shutdown/s/17000/$shut_port/g" ./tomcat7-template-version/conf/server.xml |grep shutdown
    sed  "/path=/s/location/$urllocation/g" ./tomcat7-template-version/conf/server.xml |grep path=
    fi
echo "##########################"
echo "##########################"
#read -n 1 -p "Please confirm the above configuration is correct,If the correct,Press any key to continue..."
if [ $# -eq 6 ];then
    newname=$1
    start_port=$2
    shut_port=$3
    tomcat_version=$4
    urllocation=$6
    sed -i "/APP=/s/experss/$newname/g" ./tomcat7-template-version/bin/env.sh
    sed -i "/CATALINA_HOME=/s/tomcat/$tomcat_version/g" ./tomcat7-template-version/bin/env.sh |grep CATALINA_HOME=
    sed -i "/docBase=/s/experss/$newname/g" ./tomcat7-template-version/conf/server.xml
    sed -i "/protocol/s/7000/$start_port/g" ./tomcat7-template-version/conf/server.xml
    sed -i "/shutdown/s/17000/$shut_port/g" ./tomcat7-template-version/conf/server.xml
    sed -i "/path=/s/location/$urllocation/g" ./tomcat7-template-version/conf/server.xml 
    fi
echo "##########################"
echo "##########################"
cat ./tomcat7-template-version/bin/env.sh
grep protocol ./tomcat7-template-version/conf/server.xml
grep shutdown ./tomcat7-template-version/conf/server.xml
grep docBase ./tomcat7-template-version/conf/server.xml
echo "##########################"
echo "##########################"
echo "Now generates the configuration file............."
echo "##########################"
mv tomcat7-template-version tomcat-$app_name-$nowdate
zip -r tomcat-$app_name-$nowdate.zip tomcat-$app_name-$nowdate/
#cp tomcat-$app_name-$nowdate.zip /export/fjrpkgs/
echo "The tomcat configuration file is:  "
ls -lh /export/adminpkgs/tomcat-$app_name-$nowdate.zip
mv ./tomcat-$app_name-$nowdate* ./zipbck/
echo "curl --connect-timeout 5 -d \"aid=$5&appv=tomcat-$app_name-$nowdate\" http://60.205.181.49:19888/ops/api/add_appv/"
curl --retry 3 --connect-timeout 10 -d "aid=$5&appv=tomcat-$app_name-$nowdate" http://60.205.181.49:19888/ops/api/add_appv/
echo "##########################"
echo "The configuration file generation completed !"
echo "##########################"
echo "===================================================="
echo "====**              End                    **======="
echo "====** Configuration file generation completed**===="
echo "===================================================="
