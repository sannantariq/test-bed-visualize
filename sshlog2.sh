#!/usr/bin/expect
spawn ssh root@172.20.60.66
expect "password"
send -- "NSL4Eddie\r"
sleep 5
send -- "pwd\r"
interact