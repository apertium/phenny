#!/bin/bash
message="$*"
echo -n "$message "
openssl dgst -sign ~/.phenny/id_rsa <(echo "$message") | base64 -w 0
echo
