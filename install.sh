#!/usr/bin/env bash
#------------------------------------------------
# Installation script for botany
# Please run as superuser
#------------------------------------------------

PREFIX="/usr"

error_exit() {
    echo -e "Botany Install: ${1:-"Unknown Error"}" >&2
    exit 1
}

[[ $(id -u) != 0 ]] && error_exit "You must be root to run this script."

cp -r $PWD $PREFIX/share/
chmod 755 $PREFIX/share/botany
rm -f $PREFIX/share/botany/install.sh
chmod 755 $PREFIX/share/botany/art
chmod 644 $PREFIX/share/botany/art/*
chmod 644 $PREFIX/share/botany/*.py
chmod 755 $PREFIX/share/botany/botany.py
chmod 666 $PREFIX/share/botany/testsql.py

ln -s $PREFIX/share/botany/botany.py $PREFIX/bin/botany

$PREFIX/bin/botany &
sleep 3
pkill botany

chmod 755 $PREFIX/share/botany/sqlite
chmod 666 $PREFIX/share/botany/sqlite/garden_db.sqlite

echo "Botany has been installed! Simply run 'botany' to get started!"
