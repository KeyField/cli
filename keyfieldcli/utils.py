
import time
from datetime import datetime, timezone

from .localstorage import LocalStorage

def get_timestamp_seconds():
    ts = time.time()
    return int(ts)

def timestamp_to_datetime(ts):
    x = datetime.fromtimestamp(ts, tz=timezone.utc)
    return x

def to_local_tz(dt):
    return dt.astimezone()

def get_username(args):
    if 'username' not in args:
        device_storage = LocalStorage('device')
        with device_storage as ds:
            return ds["username"]
    else:
        return args.username
