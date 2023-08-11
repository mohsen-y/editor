from functools import lru_cache
from typing import Dict

locks = {}

@lru_cache()
def get_locks() -> Dict:
    return locks
