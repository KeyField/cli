
from nacl.signing import SigningKey, VerifyKey
from nacl.encoding import URLSafeBase64Encoder

from ..utils import get_timestamp_seconds
from ..localstorage import LocalStorage


def validate_current_user_key(id_block: dict, current_trusted_key: VerifyKey):
    """Walk through the user's previous_keys from the current_trusted_key up to
    the current main key, raising an error if any link fails to validate.

    This chain is built by the user key rotation function which creates a new
    user main key and signs it into effect with the old one, appending it.

    The chain MUST be linear by timestamp (dict key). More than one keypair per
    second is invalid, which is impossible because it's a dict key.

    Once the newer main key is valid clients should update their model so that
    the newest key is always used, and older keys are only used for old content.

    Returns a VerifyKey of the current user key if it is trusted.
    """

    previous_keys = sorted(
        id_block['previous_keys'].items(),
        key=lambda x: x[0]
    )
    for timestamp, keypair in previous_keys:
        print(f"key ts {timestamp}")
        # TODO
