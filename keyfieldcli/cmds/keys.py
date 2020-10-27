
from nacl.signing import SigningKey, VerifyKey
from nacl.public import PrivateKey, PublicKey
from nacl.encoding import URLSafeBase64Encoder

from ..utils import get_timestamp_seconds
from ..localstorage import LocalStorage

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
        return VerifyKey(_get_user_signingkey(username).verify_key)

def _get_user_publickey(username):
    user_storage = LocalStorage(username, readonly=True)
    with user_storage as us:
        return PublicKey(_get_user_privatekey(username).public_key.encode())

def _get_device_privatekey():
    device_storage = LocalStorage('device')
    with device_storage as ds:
        return PrivateKey(ds["privatekey"])

def _get_device_publickey():
    privkey = _get_device_privatekey()
    return PublicKey(privkey.public_key.encode())

def new_user(args):
    """Creates a brand new KeyField user identity.
    """
    if not args.username.isprintable():
        raise ValueError(f"Username must be text characters.")
    # TODO check username against spec
    username = args.username
    if LocalStorage.exists(username):
        print("It appears this user has already been initialized:")
        print(f"User {username} with public key {_get_user_publickey(username).encode(URLSafeBase64Encoder)}")
        if not args.force:
            print(f"Pass --force to overwrite and create a new user identity.")
            return
        else:
            print(f"Overwriting data for {username}")
    LocalStorage.create_new_storage(username)
    user_storage = LocalStorage(username)
    device_storage = LocalStorage('device')
    with user_storage as us, device_storage as ds:
        us["username"] = username
        ds["username"] = username
        us["homeserver"] = ""
        us["signingkey"] = SigningKey.generate().encode()
        us["privatekey"] = PrivateKey.generate().encode()
        us["previous_keys"] = {
            get_timestamp_seconds(): {
                "signingkey": us["signingkey"],
                "privatekey": us["privatekey"],
            }
        }
        us["devices"] = {
            ds["devicename"]: {
                "added": get_timestamp_seconds(),
                "publickey": _get_device_publickey().encode(),
            }
        }
    print(f"Identity created: {_get_user_publickey(username).encode(URLSafeBase64Encoder)} with username {username}")

def rotate_user_key():
    """Rotates the user main key.

    Required when a device was removed to keep future content safe.
    """
    pass

def new_device(args):
    """Creates a device key set, might not be attached to a user yet.
    """
    if LocalStorage.exists('device'):
        print("It appears this device has already been initialized:")
        device_localstorage = LocalStorage('device')
        with device_localstorage as ds:
            print(f"Device {ds['devicename']} with public key {_get_device_publickey().encode(URLSafeBase64Encoder)}")
        if not args.force:
            print(f"Pass --force to overwrite and create a new device key.")
            return
        else:
            print(f"Overwriting previous device data...")
    devicename = args.devicename
    LocalStorage.create_new_storage('device')
    device_localstorage = LocalStorage('device')
    with device_localstorage as ds:
        ds["username"] = ""
        ds["privatekey"] = PrivateKey.generate().encode()
        ds["devicename"] = devicename
    print(f"Created device {devicename} with public key {_get_device_publickey().encode(URLSafeBase64Encoder)}")
