
"""
User commands are local commands only.

For interacting with your homeserver see the account commands.
"""

import sys
import json

from nacl.signing import VerifyKey, SigningKey
from nacl.public import PublicKey, PrivateKey
from nacl.encoding import URLSafeBase64Encoder
import msgpack

from ..crypto.common import (
    _build_profile_block,
    _get_user_verifykey,
    _get_user_publickey,
    _get_user_signingkey,
)
from ..utils import (
    get_timestamp_seconds, timestamp_to_datetime, to_local_tz, get_username
)
from ..localstorage import LocalStorage

def user_info(args):
    username = get_username(args)

    user_storage = LocalStorage(username, readonly=True)
    with user_storage as us:
        print(f"User Identity {_get_user_verifykey(username).encode(URLSafeBase64Encoder)} / {us['username']}")
        print(f"Public encryption key: {_get_user_publickey(username).encode(URLSafeBase64Encoder)}")
        print(f"Devices ({len(us['devices'])}):")
        for k,v in us['devices'].items():
            dt = timestamp_to_datetime(v['added'])
            print(f"  Device {k} public key: {PublicKey(v['publickey']).encode(URLSafeBase64Encoder)} added {to_local_tz(dt)}")

def user_profile(args):
    username = get_username(args)
    pb = _build_profile_block(username)
    if args.export:
        packd = msgpack.packb(pb)
        signed = keys._get_user_signingkey(username).sign(packd)
        with open(args.export, 'wb') as f:
            f.write(signed)
        print(f"Wrote signed and packed profile to {args.export}", file=sys.stderr)
    else:
        print(json.dumps(pb, indent=2, sort_keys=True))
