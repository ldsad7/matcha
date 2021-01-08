#!/bin/bash

echo "\033[31mLet's start!\033[0m"

echo '\033[32msetting variables and credentials...\033[0m'
user='root'
password='password'
database='pmt'
domain='yandex.ru'
name='127.0.0.1:8000'
py='/Users/tsimonis/Desktop/projects/matcha/myvenv/bin/python'
script=$(readlink "$0")
scriptpath=$(dirname "$SCRIPT")

echo '\033[32mcopying large or secret files into new directory...\033[0m'
cp ~/local_settings.py $scriptpath/dating_site
cp ~/GeoLite2-City.mmdb $scriptpath/geoip
cp ~/GeoLite2-Country.mmdb $scriptpath/geoip

echo '\033[32mcreating venv myvenv...\033[0m'
if [ ! -d "myvenve" ]; then
    $py -m venv myvenv
fi

echo '\033[32mactivating myvenv...\033[0m'
source ./myvenv/bin/activate

echo '\033[32minstalling necessary libraries...\033[0m'
$py -m pip install -r requirements.txt
brew update
brew install libmaxminddb

echo '\033[32mcreating database...\033[0m'
mysql --user="$user" --password="$password" --database="$database" --execute="drop database if exists $database; create database $database;"

echo '\033[32mmigrating tables...\033[0m'
$py manage.py migrate

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