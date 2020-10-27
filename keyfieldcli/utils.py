
from datetime import datetime, timezone

def get_timestamp_seconds():
    ts = datetime.utcnow()
    return int(ts.timestamp())
