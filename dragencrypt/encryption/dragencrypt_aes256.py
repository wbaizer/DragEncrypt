import base64
import functools
import getpass
import json
import sys


# Borrowed from https://bitbucket.org/brendanlong/python-encryption/src/1737e959fa307d84a5dcf96c4139b1d91a08b2e9/encryption.py?fileviewer=file-view-default

try:
    import Crypto
except ImportError:
    print "  --- Please run pip install pycrypto"
    sys.exit(1)

from Crypto.Cipher import AES
from Crypto.Hash import HMAC, SHA256
from Crypto.Protocol.KDF import PBKDF2
from Crypto import Random

def make_keys(password, salt=None, iterations=100000):
    """Generates two 128-bit keys from the given password using
       PBKDF2-SHA256.
       We use PBKDF2-SHA256 because we want the native output of PBKDF2 to be
       256 bits. If we stayed at the default of PBKDF2-SHA1, then the entire
       algorithm would run twice, which is slow for normal users, but doesn't
       slow things down for attackers.
       password - The password.
       salt - The salt to use. If not given, a new 8-byte salt will be generated.
       iterations - The number of iterations of PBKDF2 (default=100000).

       returns (k1, k2, salt, interations)
    """
    if salt is None:
        # Generate a random 16-byte salt
        salt = Random.new().read(16)

    # Generate a 32-byte (256-bit) key from the password
    prf = lambda p,s: HMAC.new(p, s, SHA256).digest()
    key = PBKDF2(password, salt, 32, iterations, prf)

    # Split the key into two 16-byte (128-bit) keys
    return key[:16], key[16:], salt, iterations

def encrypt(message, key):
    """Encrypts a given message with the given key, using AES-CFB.
       message - The message to encrypt (byte string).
       key - The AES key (16 bytes).

       returns (ciphertext, iv). Both values are byte strings.
    """
    # The IV should always be random
    bs = AES.block_size
    salt = Random.new().read(bs - len('Salted__'))

    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CFB, iv)
    ciphertext = cipher.encrypt(message)
    return (ciphertext, iv)


def decrypt(ciphertext, key, iv):
    """Decrypts a given ciphertext with the given key, using AES-CFB.
       message - The ciphertext to decrypt (byte string).
       key - The AES key (16 bytes).
       iv - The original IV used for encryption.

       returns The cleartext (byte string)
    """
    cipher = AES.new(key, AES.MODE_CFB, iv)
    msg = cipher.decrypt(ciphertext)
    return msg

def make_hmac(message, key):
    """Creates an HMAC from the given message, using the given key. Uses
       HMAC-MD5.
       message - The message to create an HMAC of.
       key - The key to use for the HMAC (at least 16 bytes).

       returns A hex string of the HMAC.
    """
    h = HMAC.new(key)
    h.update(message)
    return h.hexdigest()

