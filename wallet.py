
import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import binascii

class Wallet(object):
    """
    A wallet is a private/public key pair
    """
    def __init__(self):
        random_gen = Crypto.Random.new().read
        self._private_key = RSA.generate(1024, random_gen)
        self._public_key = self._private_key.publickey()
        self._signer = PKCS1_v1_5.new(self._private_key)
        
    @property
    def address(self):
        """We take a shortcut and say address is public key"""
        return binascii.hexlify(self._public_key.exportKey(format='DER')).decode('ascii')
    
    def sign(self, message):
        """
        Sign a message with this wallet
        """
        h = SHA.new(message.encode('utf8'))
        return binascii.hexlify(self._signer.sign(h)).decode('ascii')
    
    
def verify_signature(wallet_address, message, signature):
    """
    Check that the provided `signature` corresponds to `message`
    signed by the wallet at `wallet_address`
    """
    pubkey = RSA.importKey(binascii.unhexlify(wallet_address))
    verifier = PKCS1_v1_5.new(pubkey)
    h = SHA.new(message.encode('utf8'))
    return verifier.verify(h, binascii.unhexlify(signature))
