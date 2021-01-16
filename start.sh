#!/bin/bash

echo "\033[31mLet's start!\033[0m"

echo '\033[32msetting variables and credentials...\033[0m'
user='root'
password='password'
database='pmt'
domain='yandex.ru'
name='127.0.0.1:8000'
site_name='dating_site'
scriptpath="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
py='$basedir/myvenv/bin/python'
mysql_file_1="$scriptpath/myvenv/lib/python3.8/site-packages/django/db/backends/mysql/operations.py"
mysql_file_2="$scriptpath/myvenv/lib/python3.8/site-packages/django/db/backends/mysql/base.py"

echo '\033[32mcopying large or secret files into our folder...\033[0m'
cp ~/local_settings.py $scriptpath/$site_name

echo '\033[32mcreating venv myvenv...\033[0m'
if [ ! -d "myvenv" ]; then
    $py -m venv myvenv
    sed -i '' "s/query = query.decode(errors='replace')/query = errors='replace'/" $mysql_file_1
    sed -i '' "s/raise ImproperlyConfigured('mysqlclient 1.3.13 or newer is required; you have %s.' % Database.__version__)/pass/" $mysql_file_2
fi

sed -i "s/query = query.decode(errors='replace')/query = errors='replace'/" $mysql_file_1
sed -i "s/raise ImproperlyConfigured('mysqlclient 1.3.13 or newer is required; you have %s.' % Database.__version__)/pass = errors='replace'/" $mysql_file_2

echo '\033[32mactivating myvenv...\033[0m'
source ./myvenv/bin/activate

echo '\033[32minstalling necessary libraries...\033[0m'
$py -m pip install -r requirements.txt

echo '\033[32mlaunching mysql...\033[0m'
mysqld_safe --skip-grant-tables
brew services start mysql
mysql.server start

echo '\033[32mcreating database...\033[0m'
mysql --user="$user" --password="$password" --execute="drop database if exists $database; create database $database;"

echo '\033[32mmigrating tables...\033[0m'
$py manage.py migrate

echo '\033[32collecting static and media files...\033[0m'
$py manage.py collectstatic --no-input

echo '\033[32mupdating a record in django_site table...\033[0m'
mysql --user="$user" --password="$password" --database="$database" --execute="update django_site set domain='$domain', name='$name' where id=1;"

echo '\033[32mfilling database...\033[0m'
$py manage.py inflate_db

echo '\033[32mlaunching redis...\033[0m'
brew install redis
redis-server stop
brew services restart redis

echo '\033[32mrunning server...\033[0m'
$py manage.py runserver

echo '\033[32mlaunching celery...\033[0m'
celery -A dating_site worker -l info &
celery -A dating_site beat -l info &
