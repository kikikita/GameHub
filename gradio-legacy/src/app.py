import subprocess
import time
import atexit
import shutil
from redis import Redis, ConnectionError


REDIS_BIN = shutil.which("redis-server")

if not REDIS_BIN:
    raise RuntimeError("redis-server not found. Ensure redis is installed via packages.txt")


redis_cmd = [
    REDIS_BIN,
    "--save",
    "",
    "--appendonly",
    "no",
    "--dir",
    "/tmp",
    "--pidfile",
    "/tmp/redis.pid",
]
redis_process = subprocess.Popen(redis_cmd)


redis_client = Redis()
for _ in range(20):
    try:
        redis_client.ping()
        break
    except ConnectionError:
        time.sleep(0.5)
else:
    raise RuntimeError("Failed to start redis-server")


atexit.register(redis_process.terminate)


time.sleep(0.5)

import main
