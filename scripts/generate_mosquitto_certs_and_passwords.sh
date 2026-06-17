#!/bin/bash
# Generate self-signed CA and server cert for local testing (openssl must be installed)
set -e
OUT_DIR="$(pwd)/mosquitto/config"
mkdir -p "$OUT_DIR"

# CA
openssl genrsa -out "$OUT_DIR/ca.key" 2048
openssl req -x509 -new -nodes -key "$OUT_DIR/ca.key" -sha256 -days 3650 -out "$OUT_DIR/ca.crt" -subj "/CN=LocalMosquittoCA"

# Server key and CSR
openssl genrsa -out "$OUT_DIR/server.key" 2048
openssl req -new -key "$OUT_DIR/server.key" -out "$OUT_DIR/server.csr" -subj "/CN=mosquitto.local"

# Sign server cert
openssl x509 -req -in "$OUT_DIR/server.csr" -CA "$OUT_DIR/ca.crt" -CAkey "$OUT_DIR/ca.key" -CAcreateserial -out "$OUT_DIR/server.crt" -days 365 -sha256

# Create mosquitto password file (requires mosquitto_passwd utility)
MOSQUITTO_PASSWD=$(which mosquitto_passwd || true)
if [ -n "$MOSQUITTO_PASSWD" ]; then
  # create a user 'device' with password 'devicepass' (change in production)
  "$MOSQUITTO_PASSWD" -c -b "$OUT_DIR/passwords" device devicepass
  echo "Created password file at $OUT_DIR/passwords (user=device, pass=devicepass)"
else
  echo "mosquitto_passwd not found. Please install mosquitto-clients and run:\n mosquitto_passwd -c /path/to/mosquitto/config/passwords device"
fi

echo "Generated certs in $OUT_DIR"
