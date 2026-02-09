"""トークンブラックリスト（インメモリ実装）"""

import time
from threading import Lock

_blacklist: dict[str, float] = {}  # token -> expiry timestamp
_lock = Lock()


def blacklist_token(token: str, expires_at: float) -> None:
    """トークンをブラックリストに追加"""
    with _lock:
        _blacklist[token] = expires_at
        _cleanup()


def is_blacklisted(token: str) -> bool:
    """トークンがブラックリストに含まれているか"""
    with _lock:
        if token in _blacklist:
            if _blacklist[token] > time.time():
                return True
            del _blacklist[token]
    return False


def _cleanup() -> None:
    """期限切れエントリを削除"""
    now = time.time()
    expired = [t for t, exp in _blacklist.items() if exp <= now]
    for t in expired:
        del _blacklist[t]
