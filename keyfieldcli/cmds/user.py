
import sys
from nacl.signing import VerifyKey, SigningKey
from nacl.public import PublicKey, PrivateKey
from nacl.encoding import URLSafeBase64Encoder
import json
import msgpack

from ..utils import (
    get_timestamp_seconds, timestamp_to_datetime, to_local_tz, get_username
)
from ..localstorage import LocalStorage
from . import keys

def user_info(args):
    username = get_username(args)

    user_storage = LocalStorage(username, readonly=True)
    with user_storage as us:
        print(f"User Identity {keys._get_user_verifykey(username).encode(URLSafeBase64Encoder)} / {us['username']}")
        print(f"Public encryption key: {keys._get_user_publickey(username).encode(URLSafeBase64Encoder)}")
        print(f"Devices ({len(us['devices'])}):")
        for k,v in us['devices'].items():
            dt = timestamp_to_datetime(v['added'])
            print(f"  Device {k} public key: {PublicKey(v['publickey']).encode(URLSafeBase64Encoder)} added {to_local_tz(dt)}")

def _build_profile_block(username):
    pb = {} # profile block
    pb['timestamp_signed'] = get_timestamp_seconds()
    user_storage = LocalStorage(username, readonly=True)
    with user_storage as us:
        pb['username'] = us['username']
        pb['homeserver'] = us['homeserver']
        # WARNING do not accidentally leak keys here
        pb['keys'] = {
            'verify': keys._get_user_verifykey(us['username']).encode(URLSafeBase64Encoder).decode('utf-8'),
            'public': keys._get_user_publickey(us['username']).encode(URLSafeBase64Encoder).decode('utf-8'),
        }
        pb['previous_keys'] = {
            k: {
                'verify': VerifyKey(SigningKey(v['signingkey']).verify_key.encode()).encode(URLSafeBase64Encoder).decode('utf-8'),
                'public': PublicKey(PrivateKey(v['privatekey']).public_key.encode()).encode(URLSafeBase64Encoder).decode('utf-8'),
            } for k, v in us['previous_keys'].items()
        }
        # end WARNING
    return pb

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
