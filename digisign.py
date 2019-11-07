"""digicheck - create and verify signatures for files

Usage:
  digicheck keys
  digicheck public <keyfilename>
  digicheck sign <filename> <keyfilename>
  digicheck check <filename> <keyfilename> <signaturefilename>
  digicheck (-h | --help)
  digicheck --version

Use the command-line to first create a key pair, then a
signature for a file, and finally when you need to make
sure file has not been tampered with in the meantime,
check that the signatures are still equal.

Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import sys
import docopt

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto import Random

def generate_keys():
   random_generator = Random.new().read
   key = RSA.generate(2048, random_generator)
   return (key.exportKey(), key.publickey().exportKey())

def generate_hash(data):
   return SHA256.new(data).digest()

def generate_signature(hash, key):
   return key.sign(hash, '')

def verify_signature(hash, public_key, signature):
   return public_key.verify(hash, signature)

def gen_keys():
    private, public = generate_keys()
    
    with open("private.pem", "wb") as prv_file:
        prv_file.write(private)
    
    with open("public.pem", "wb") as pub_file:
        pub_file.write(public)

    
    print(private)
    print()
    print()
    print(public)
'''
    Digitally sign files.
    Arguments:
        - filename: string => Name of the file (pdf certificate) to be signed
        - private_key_filename: string => Name of the file which stores the private key
    Returns:
        - Digital signature: string => Digital signature signed with private key
'''
def sign_file(filename, private_key_filename):
    
    with open(filename, "rb") as signedfile:
        hash = SHA256.new()
        hash.update(signedfile.read())
    
    with open(private_key_filename, "rb") as keyfile:
        private_key = RSA.importKey(keyfile.read())
        private_key = PKCS1_v1_5.new(private_key)

    print(type(private_key))
    print(type(hash))

    result = private_key.sign(hash)
    return result

'''
    Check if digital signature is valid.
    Arguments:
        - signed_filename: string => Name of file (pdf certificate) which has already been signed by author
        - public_key_filename: string => Name of the file which store the public key of author of pdf
        - digital_signature: string => Digital signature signed with private key of author
    Return:
        - Validity: boolean => Returns True if valid digital signature
'''
def check_valid_sign(signed_filename, public_key_filename, digital_signature):

    with open(signed_filename, "rb") as signedfile:
        hash = SHA256.new()
        hash.update(signedfile.read())

    with open(public_key_filename, "rb") as keyfile:
        public_key = RSA.importKey(keyfile.read())
        public_key = PKCS1_v1_5.new(public_key)

    print(type(hash))
    print(type(public_key))
    print(type(digital_signature))

    if public_key.verify(hash, digital_signature):
        return True
    else:
        return False