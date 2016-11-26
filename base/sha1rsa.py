# -*- coding: utf-8 -*-
# required `M2Crypto' (http://sandbox.rulemaker.net/ngps/m2/)

from M2Crypto import RSA
import binascii

import sys
if sys.version[:3] == '2.4':
    import sha
    sha1_func = sha.sha
else:
    import hashlib
    sha1_func = hashlib.sha1


__all__ = ['sign', 'verify']

def sign(data, key_file):
    """sign

    @param data: data to be signed
    @param key_file: private key file path
    @return: a hex string which is the signature
    """
    pri_key = RSA.load_key(key_file)
    digest = sha1_func(data).digest()
    signature = pri_key.sign(digest)
    return binascii.hexlify(signature)

def verify(data, hex_signature, key_file):
    """verify

    @param data: data content to be verified
    @param hex_signature: a hex string which is the signature
    @param key_file: public key file path
    @return: True or False, depending on whether the signature was verified
    """
    pub_key = RSA.load_pub_key(key_file)
    digest = sha1_func(data).digest()
    try:
        signature = binascii.unhexlify(hex_signature)
    except TypeError:
        return False

    try:
        res = pub_key.verify(digest, signature)
    except RSA.RSAError:
        return False

    return res
