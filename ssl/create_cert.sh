#!/bin/bash

# Call this script to create a new certificate, signed by the BugHog CA.
# Provide one parameter: the domain name of the certificate you want to create.

# The script will ask you for several things (country, state, etc.), but the only thing that really matters is the Common Name.
# This should be the domain name of the certificate you want to create. Other fields can be left blank.
# Finally, the script will sign the certificate with the CA key, for which you will need to provide the CA password `dnet`.

NAME=$1
openssl genrsa -out $NAME.key 2048
openssl req -new -key $NAME.key -out $NAME.csr
>$NAME.ext cat <<-EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names
[alt_names]
DNS.1 = $NAME # Be sure to include the domain name here because Common Name is not so commonly honoured by itself
DNS.2 = bar.$NAME # Optionally, add additional domains (I've added a subdomain here)
IP.1 = 192.168.0.13 # Optionally, add an IP address (if the connection which you have planned requires it)
EOF
openssl x509 -req -in $NAME.csr -CA bughog_ca.pem -CAkey bughog_ca.key -CAcreateserial \
-out $NAME.crt -days 7300 -sha256 -extfile $NAME.ext
# Valid for 20 years. A higher number of days could could cause issues with some software.
