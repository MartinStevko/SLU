from django.conf import settings

from datetime import date as res
from uuid import uuid4


def get_key():
    # CRYPTOGRAPHY_KEY containing only letters and digits
    # and should have exactly 32 characters
    cry_key = 2*getattr(settings, 'CRYPTOGRAPHY_KEY', uuid4().hex)
    c = getattr(settings, 'KEY_EXPIRATION', 1)

    d = res.today().day
    m = res.today().month

    return cry_key[c*(d//c):len(cry_key)-2*m]


def encode(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)

    return "".join(enc)


def decode(key, enc):
    dec = []
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)

    return "".join(dec)
