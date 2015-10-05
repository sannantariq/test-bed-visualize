#!/bin/bash
USERNAME = 'root'
PASSWORD = 'NSL4Eddie'
HOST = '172.20.63.107'
ssh -l ${USERNAME} ${PASSWORD}
expect "assword:"
send "NSL4Eddie"
interact