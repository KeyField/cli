
import time
from datetime import datetime, timezone

def get_timestamp_seconds():
    ts = time.time()
    return int(ts)

def timestamp_to_datetime(ts):
    x = datetime.fromtimestamp(ts, tz=timezone.utc)
    return x

def to_local_tz(dt):
    return dt.astimezone()
