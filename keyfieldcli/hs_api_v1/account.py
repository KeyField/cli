
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
