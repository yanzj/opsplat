#!/bin/bash

timestaps=`date +%Y%m%dT%H%M`
echo "cd $1"
cd $1 
filename=`ls *.war`
if [ $? -eq 0 ]
 then
 echo "target file is $filename"
 echo "mkdir $2-$timestaps"
 mkdir $2-$timestaps
 echo "unzip -o $filename -d $2-$timestaps/"
 unzip -o $filename -d $2-$timestaps/
 echo "zip -q -r $2-$timestaps.zip $2-$timestaps"
 zip -q -r $2-$timestaps.zip $2-$timestaps
 echo "mv $2-$timestaps.zip /export/content/"
 mv $2-$timestaps.zip /export/content/
 if [ $? -eq 0 ]
  then
    echo "curl --connect-timeout 5 -d \"appname=$2&filename=$2-$timestaps&dest=$3&branch=$4\" http://60.205.111.222:19888/ops/api/addappversion/"
  curl --connect-timeout 5 -d "appname=$2&filename=$2-$timestaps&dest=$3&branch=$4" http://60.205.111.222:19888/ops/api/addappversion/
 fi
 echo "$filename change to /export/content/$2-$timestaps.zip"
else
 echo "war文件不存在,检测tar.gz文件"
 filename=`ls *.tar.gz`
 if [ $? -eq 0 ]
  then
   echo "target file is $filename"
   echo "mkdir $2-$timestaps"
   mkdir $2-$timestaps
   echo "tar xf $filename -C $2-$timestaps/"
   tar xf $filename -C $2-$timestaps/
   echo "zip -q -r $2-$timestaps.zip $2-$timestaps"
   zip -q -r $2-$timestaps.zip $2-$timestaps
   echo "mv $2-$timestaps.zip /export/content/"
   mv $2-$timestaps.zip /export/content/
   if [ $? -eq 0 ]
    then
    echo "curl --connect-timeout 5 -d \"appname=$2&filename=$2-$timestaps&dest=$3&branch=$4\" http://60.205.111.222:19888/ops/api/addappversion/"
     curl --retry 3 --connect-timeout 10 -d "appname=$2&filename=$2-$timestaps&dest=$3&branch=$4" http://60.205.111.222:19888/ops/api/addappversion/
   fi
   echo "$filename change to /export/content/$2-$timestaps.zip"
 else
  echo "tar.gz文件也不存在"
  exit 1
 fi
fi


