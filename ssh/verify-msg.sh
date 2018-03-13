#!/bin/bash
message="${@:1:$#-1}"
signature="${@: -1}"
public_key="$(ssh-keygen -e -f ~/.phenny/id_rsa.pub -m PKCS8)"
openssl dgst -verify <(echo "$public_key") -signature <(echo "$signature" | base64 -d) <(echo "$message")
