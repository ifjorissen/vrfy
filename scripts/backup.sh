#!/bin/sh 

#This script should be run from the root of the project (i.e home/vrfy/vrfy/)

echo 'activating the environment.'
. $HOME/py_env/bin/activate
#source $HOME/Envs/vrfy/bin/activate

cd $HOME/vrfy

#django db / asset backup commands
echo 'performing db and media backup commands ...'
python3 manage.py dbbackup
python3 manage.py mediabackup

#location, location

#bk_loc="/Users/ifjorissen/vrfy_proj/vrfy_backups"
bk_loc="/home/vrfy/vrfy_backups"

#old filename
echo 'renaming files'
dbbk_oldname="default.backup"
dir_date=`date "+%Y-%m-%d"`
file_date=`date "+%Y-%m-%d-%H"`

#db_dir_path=$bk_loc/$dir_date
#mkdir -p $db_dir_path
file_name="$file_date"_"$USER"_db_backup.tar.gz

echo "tar-ing $bk_loc/$dbbk_oldname to $bk_loc/$file_name"
tar -czf $bk_loc/$file_name $bk_loc/$dbbk_oldname
rm $bk_loc/$dbbk_oldname

#echo "moving files to $db_dir_path ..."
#mv $bk_loc/*.tar.gz $db_dir_path
echo 'all done!'