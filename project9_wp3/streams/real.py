"""Real streams (R1, R2): read a log file line by line and take one field per line.

Example (NASA-style web access log, the client host is the first field):
    items, true_count = load_log("NASA_access_log_Jul95", field=0)
Any public log works; name its source and licence in the report.
"""
import gzip
import io


def iter_log(path: str, field: int = 0, sep=None, limit=None, encoding="latin-1"):
    """Yield the chosen field of each line (lines that are too short are skipped)."""
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rb") as raw:
        for i, line in enumerate(io.TextIOWrapper(raw, encoding=encoding, errors="replace")):
            if limit is not None and i >= limit:
                break
            parts = line.split(sep)
            if len(parts) > field:
                yield parts[field]


def load_log(path: str, field: int = 0, sep=None, limit=None):
    items = list(iter_log(path, field, sep, limit))
    return items, len(set(items))
