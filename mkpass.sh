#!/bin/bash
create_length=`echo "$1*5" | /usr/bin/bc`
password_length=`echo "$1+1" | /usr/bin/bc`
/usr/bin/pwgen -s $create_length 1 | tr -d 0OI1 | /usr/bin/tail --bytes $password_length
