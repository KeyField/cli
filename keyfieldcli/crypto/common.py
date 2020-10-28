
from nacl.signing import SigningKey, VerifyKey
from nacl.public import PrivateKey, PublicKey, Box, SealedBox
from nacl.encoding import URLSafeBase64Encoder

from ..localstorage import LocalStorage
from ..utils import get_timestamp_seconds


def _get_user_signingkey(username):
    user_storage = LocalStorage(username, readonly=True)
    with user_storage as us:
        return SigningKey(us["signingkey"])

def _get_user_privatekey(username):
    user_storage = LocalStorage(username, readonly=True)
    with user_storage as us:
        return PrivateKey(us["privatekey"])

def _get_user_verifykey(username):
    user_storage = LocalStorage(username, readonly=True)
    with user_storage as us:
        return VerifyKey(_get_user_signingkey(username).verify_key.encode())

def _get_user_publickey(username):
    user_storage = LocalStorage(username, readonly=True)
    with user_storage as us:
        return PublicKey(_get_user_privatekey(username).public_key.encode())

def _get_homeserver_box(username):
    """Get the box shared between the user and their homeserver."""
    u_privkey = _get_user_privatekey(username)
    user_storage = LocalStorage(username, readonly=True)
    with user_storage as us:
        s_pubkey = PublicKey(us["homeserver"]["public"], URLSafeBase64Encoder)
    return Box(u_privkey, s_pubkey)

def _get_device_privatekey():
    device_storage = LocalStorage('device', readonly=True)
    with device_storage as ds:
        return PrivateKey(ds["privatekey"])

def _get_device_publickey():
    privkey = _get_device_privatekey()
    return PublicKey(privkey.public_key.encode())

def _build_profile_block(username):
    """Builds the PUBLIC identity block that can be distributed.
    """
    pb = {} # profile block
    pb['timestamp_signed'] = get_timestamp_seconds()
    user_storage = LocalStorage(username, readonly=True)
    with user_storage as us:
        pb['username'] = us['username']
        pb['homeserver'] = us['homeserver']
        # WARNING do not accidentally leak keys here
        pb['keys'] = {
            'verify': _get_user_verifykey(us['username']).encode(URLSafeBase64Encoder).decode('utf-8'),
            'public': _get_user_publickey(us['username']).encode(URLSafeBase64Encoder).decode('utf-8'),
        }
        # TODO construct sigchain
        pb['previous_keys'] = {
            k: {
                'verify': VerifyKey(SigningKey(v['signingkey']).verify_key.encode()).encode(URLSafeBase64Encoder).decode('utf-8'),
                'public': PublicKey(PrivateKey(v['privatekey']).public_key.encode()).encode(URLSafeBase64Encoder).decode('utf-8'),
            } for k, v in us['previous_keys'].items()
        }
        # end WARNING
        # TODO device list
    return pb
