#!/bin/bash

openssl genrsa -des3 -out bughog_ca.key 2048
openssl req -x509 -new -nodes -key bughog_ca.key -sha256 -days 7300 -out bughog_ca.pem
# Valid for 20 years. A higher number of days could could cause issues with some software.

# Make .crt
openssl x509 -outform der -in bughog_ca.pem -out bughog_ca.crt
