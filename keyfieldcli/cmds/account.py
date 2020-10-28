
import sys
import json
import base64

import requests
import msgpack
from nacl.signing import VerifyKey, SigningKey
from nacl.public import PublicKey, PrivateKey, SealedBox, Box
from nacl.encoding import URLSafeBase64Encoder

from ..utils import (
    get_timestamp_seconds, timestamp_to_datetime, to_local_tz, get_username
)
from ..localstorage import LocalStorage
from . import keys
from ..crypto.common import (
    _build_profile_block,
    _get_user_signingkey,
    _get_user_verifykey,
)
from ..hs_api_v1.homeserver import (
    get_server_advertised_verifykey,
    get_server_name,
    get_server_verified_publickey,
)


def account_register(args):
    username = get_username(args)

    if not args.public:
        server_verifykey = get_server_advertised_verifykey(args.address)
    else:
        server_verifykey = VerifyKey(args.public, URLSafeBase64Encoder)
    print(f"Server verification key: {server_verifykey.encode(URLSafeBase64Encoder).decode()}")
    server_publickey = get_server_verified_publickey(args.address, server_verifykey)

    # step 1: check access to homeserver
    server_name = get_server_name(args.address, server_verifykey)
    print(f"Server name: {server_name}")

    device_storage = LocalStorage('device', readonly=True)
    user_storage = LocalStorage(username, readonly=False)
    with user_storage as us, device_storage as ds:
        print(f"Setting identity '{username}' homeserver...")
        us['homeserver'] = {
            "address": args.address,
            "verify": server_verifykey.encode(URLSafeBase64Encoder).decode(),
            "public": server_publickey.encode(URLSafeBase64Encoder).decode(),
            "timestamp": get_timestamp_seconds()
        }
        us.save() # write changes before profile block:
        pb = _build_profile_block(username)
        # pack it:
        packd = msgpack.packb(pb)
        # sign it:
        packd_withsig = _get_user_signingkey(username).sign(packd)
        # since the server might not know us yet, we have to SealedBox:
        sbox = SealedBox(server_publickey)
        encrypted = sbox.encrypt(packd_withsig)
        # generate a signature for the headers:
        request_signature = _get_user_signingkey(username).sign(encrypted).signature

        # ready to submit the request:
        r = requests.post(
            args.address + "/api/v1/account/register",
            data=encrypted,
            headers={
                "KF-Client-Verify": _get_user_verifykey(username).encode(URLSafeBase64Encoder).decode(),
                "KF-Client-Signature": base64.urlsafe_b64encode(request_signature),
            }
        )
        if not r.ok:
            print(f"Error registering:\n{r.text}")
            # r.raise_for_status()
            return

        # box is authenticated, no need to check server signature here
        s_box = _get_homeserver_box(username)
        response_bytes = s_box.decrypt(r.content)
        unpacked = msgpack.unpackb(response_bytes)
        print(f"Server good response: {unpacked}")
        print(f"Successfully registered with homeserver.")
