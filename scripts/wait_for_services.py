import os
import sys
import time

import psycopg
from redis import Redis


def wait() -> None:
    database_url = os.environ.get("DATABASE_URL", "")
    redis_url = os.environ.get("REDIS_URL", "")
    for attempt in range(30):
        try:
            if database_url:
                with psycopg.connect(database_url):
                    pass
            if redis_url:
                Redis.from_url(redis_url).ping()
            return
        except Exception as exc:  # infrastructure startup boundary
            if attempt == 29:
                raise RuntimeError("Dependências indisponíveis") from exc
            time.sleep(1)
    sys.exit(1)


if __name__ == "__main__":
    wait()
