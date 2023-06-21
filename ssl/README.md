All website certificates should be signed by myCA.pem, and this CA should be trusted by the browser (or system).

======================================================================================================
https://stackoverflow.com/questions/7580508/getting-chrome-to-accept-self-signed-localhost-certificate
======================================================================================================

2020-05-22: With only 5 openssl commands, you can accomplish this.

Please do not change your browser security settings.

With the following code, you can (1) become your own CA, (2) then sign your SSL certificate as a CA. (3) Then import the CA certificate (not the SSL certificate, which goes onto your server) into Chrome/Chromium. (Yes, this works even on Linux.)

######################
# Become a Certificate Authority
######################

# Generate private key
openssl genrsa -des3 -out myCA.key 2048
# Generate root certificate
openssl req -x509 -new -nodes -key myCA.key -sha256 -days 825 -out myCA.pem

######################
# Create CA-signed certs
######################

NAME=mydomain.com # Use your own domain name
# Generate a private key
openssl genrsa -out $NAME.key 2048
# Create a certificate-signing request
openssl req -new -key $NAME.key -out $NAME.csr
# Create a config file for the extensions
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
# Create the signed certificate
openssl x509 -req -in $NAME.csr -CA myCA.pem -CAkey myCA.key -CAcreateserial \
-out $NAME.crt -days 825 -sha256 -extfile $NAME.ext
To recap:

Become a CA
Sign your certificate using your CA cert+key
Import myCA.pem as an Authority in your Chrome settings (Settings > Manage certificates > Authorities > Import)
Use the $NAME.crt and $NAME.key files in your server
Extra steps (for Mac, at least):

Import the CA cert at "File > Import file", then also find it in the list, right click it, expand "> Trust", and select "Always"
Add extendedKeyUsage=serverAuth,clientAuth below basicConstraints=CA:FALSE, and make sure you set the "CommonName" to the same as $NAME when it's asking for setup
You can check your work

openssl verify -CAfile myCA.pem -verify_hostname bar.mydomain.com mydomain.com.crt
