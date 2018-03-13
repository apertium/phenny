#!/bin/sh
rm -f ~/.phenny/id_rsa
rm -f ~/.phenny/id_rsa.pub
ssh-keygen -b 1024 -q -N '' -f ~/.phenny/id_rsa
