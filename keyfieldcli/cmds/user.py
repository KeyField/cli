
from nacl.public import PublicKey
from nacl.encoding import URLSafeBase64Encoder

from ..utils import get_timestamp_seconds, timestamp_to_datetime, to_local_tz
from ..localstorage import LocalStorage
from . import keys

def user_info(args):
    username = None
    if 'username' not in args:
        device_storage = LocalStorage('device')
        with device_storage as ds:
            username = ds["username"]
    else:
        username = args.username

    user_storage = LocalStorage(username, readonly=True)
    with user_storage as us:
        print(f"User Identity {keys._get_user_verifykey(username).encode(URLSafeBase64Encoder)} / {us['username']}")
        print(f"Public encryption key: {keys._get_user_publickey(username).encode(URLSafeBase64Encoder)}")
        print(f"Devices ({len(us['devices'])}):")
        for k,v in us['devices'].items():
            dt = timestamp_to_datetime(v['added'])
            print(f"  Device {k} public key: {PublicKey(v['publickey']).encode(URLSafeBase64Encoder)} added {to_local_tz(dt)}")
