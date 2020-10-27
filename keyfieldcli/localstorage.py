#!/usr/bin/env python3

import argparse
import base64
import binascii
import os
from pathlib import Path
import bson
import keyring
import nacl.secret
import nacl.utils

keyring_service = 'keyfieldcli'

class LocalStorage():
    @staticmethod
    def _get_storage_filepath(username):
        confighome = Path(os.environ.get("XDG_CONFIG_HOME", os.environ.get("HOME") + '/.config'))
        storagefile = confighome / "keyfield" / f"{username}.kfstorage"
        return storagefile

    @staticmethod
    def create_new_storage(username):
        """Creates a new local storage.

        Danger: does not care about any existing / current key.
        """
        key_bytes = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
        keyring.set_password(keyring_service, f"{username}_storagekey", base64.b64encode(key_bytes))
        box = nacl.secret.SecretBox(key_bytes)
        filepath = LocalStorage._get_storage_filepath(username)
        filepath.parent.mkdir(exist_ok=True)
        with filepath.open('wb') as f:
            d = bson.dumps({})
            enc = box.encrypt(d)
            f.write(enc)

    @staticmethod
    def exists(username):
        p = LocalStorage._get_storage_filepath(username)
        return p.exists()

    def __init__(self, username, key_bytes=None, readonly=False):
        if key_bytes is None:
            try:
                kp = keyring.get_password(keyring_service, f"{username}_storagekey")
                key_bytes = base64.b64decode(kp, validate=True)
                if len(key_bytes) != 32:
                    print(f"Error: private key in keyring is malformed.")
                    raise ValueError(f"Private key in keyring is malformed.")
            except binascii.Error as e:
                print(f"Failed to decode storage key.")
                raise
        self._box = nacl.secret.SecretBox(key_bytes)
        self.username = username
        self.storagefile = LocalStorage._get_storage_filepath(username)
        self.readonly = readonly

    def __enter__(self):
        with open(self.storagefile, 'rb') as f:
            unenc = self._box.decrypt(f.read())
            self._storage_data = bson.loads(unenc)
        return self

    def __exit__(self, type, value, traceback):
        if self.readonly:
            return
        enc = self._box.encrypt(bson.dumps(self._storage_data))
        with open(self.storagefile, 'wb') as f:
            f.write(enc)

    def __setitem__(self, item, value):
        if self.readonly:
            raise RuntimeError(f"LocalStorage<{self.username}> is readonly.")
        self._storage_data[item] = value

    def __getitem__(self, item):
        return self._storage_data[item]
