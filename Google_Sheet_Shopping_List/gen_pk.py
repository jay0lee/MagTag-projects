#!/usr/bin/env python3

### This script is meant to run on a regular Linux/MacOS device.
### It will generate the service account private key for your
### MagTag device and the public key which you'll upload to Google.
### It requires the cryptography library. Install it with:
###
### pip3 install cryptography
###
### The script can take two arguments, the first is the email address
### of your service account. The second is key size if you want a key
### larger than 1024 bytes.

### Example run:
###
### python3 gen_pk.py test-key@arcane-transit-299119.iam.gserviceaccount.com 2048
###

import datetime
import sys

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

try:
    email = sys.argv[1]
except IndexError:
    email = input('Enter your service account email address:')
try:
    key_size = int(sys.argv[2])
except IndexError:
    key_size = 1024
except ValueError:
    print(f'ERROR: key size should be a number, got {sys.argv[2]}')
    sys.exit(2)

private_key = rsa.generate_private_key(public_exponent=65537,
                                       key_size=key_size,
                                       backend=default_backend())
pn = private_key.private_numbers()
pk = (pn.public_numbers.n, pn.public_numbers.e, pn.d, pn.p, pn.q)
public_key = private_key.public_key()
builder = x509.CertificateBuilder()
builder = builder.subject_name(
    x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, email)]))
builder = builder.issuer_name(
    x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, email)]))
not_valid_before = datetime.datetime.today() - datetime.timedelta(days=1)
not_valid_after = datetime.datetime.today() + datetime.timedelta(
    days=365 * 1000 - 1)
builder = builder.not_valid_before(not_valid_before)
builder = builder.not_valid_after(not_valid_after)
builder = builder.serial_number(x509.random_serial_number())
builder = builder.public_key(public_key)
builder = builder.add_extension(x509.BasicConstraints(ca=False,
                                                      path_length=None),
                                                      critical=True)
builder = builder.add_extension(x509.KeyUsage(key_cert_sign=False,
                                              crl_sign=False,
                                              digital_signature=True,
                                              content_commitment=False,
                                              key_encipherment=False,
                                              data_encipherment=False,
                                              key_agreement=False,
                                              encipher_only=False,
                                              decipher_only=False),
                                 critical=True)
builder = builder.add_extension(x509.ExtendedKeyUsage(
    [x509.oid.ExtendedKeyUsageOID.SERVER_AUTH]),
                                 critical=True)
certificate = builder.sign(private_key=private_key,
                           algorithm=hashes.SHA256(),
                           backend=default_backend())
public_cert_pem = certificate.public_bytes(
    serialization.Encoding.PEM).decode()
print('--- upload all lines below to console.cloud.google.com ---')
print(public_cert_pem.strip())
print('--- upload all lines above to console.cloud.google.com ---')
print()

kid = input('Once the above is uploaded, copy the alphanumeric key ID value and paste here: ')
kid = kid.strip()

print()
print('--- add all lines below to secrets.py ---')
print(f'"private_key":  {pk},')
print(f'"private_key_id": "{kid}",')
print(f'"service_account_email": "{email}",')
print('--- add all lines above to secrets.py ---')
print()
