"""
API access to homeserver related endpoints.
"""

import base64

import requests
import msgpack
from nacl.signing import SigningKey, VerifyKey
from nacl.public import PrivateKey, PublicKey
from nacl.encoding import URLSafeBase64Encoder

from ..utils import (
    get_timestamp_seconds, timestamp_to_datetime, to_local_tz, get_username
)
from ..crypto.common import (
    _get_device_publickey,
    _get_device_privatekey,
    _get_user_verifykey,
    _get_user_signingkey,
    _get_user_privatekey,
)

api_base_path = '/api/v1/server'

# NOTE: not authenticated
def get_server_advertised_verifykey(address):
    r = requests.get(
        address + api_base_path + '/name'
    )
    r.raise_for_status()
    vkey_b64 = r.headers['KF-Homeserver-Verify']
    return VerifyKey(vkey_b64, URLSafeBase64Encoder)

def get_server_verified_publickey(address, verifykey):
    r = requests.get(
        address + api_base_path + '/publickey'
    )
    r.raise_for_status()
    sig = base64.urlsafe_b64decode(r.headers['KF-Homeserver-Signature'])
    mp_response = verifykey.verify(r.content, sig)
    data = msgpack.unpackb(mp_response)
    cur_time = get_timestamp_seconds()
    if abs(data['timestamp'] - cur_time) > 60:
        print(f"Server time is {cur_time - data['timestamp']} seconds behind!")
        raise ValueError("Server time is out of sync with client time!")
    return PublicKey(data['public'], URLSafeBase64Encoder)

def get_server_name(address, verifykey: VerifyKey = None):
    r = requests.get(
        address + api_base_path + '/name'
    )
    r.raise_for_status()
    sig = base64.urlsafe_b64decode(r.headers['KF-Homeserver-Signature'])
    if verifykey is None:
        verifykey = get_server_advertised_verifykey()
    mp_response = verifykey.verify(r.content, sig)
    name = msgpack.unpackb(mp_response)
    return name.decode()
