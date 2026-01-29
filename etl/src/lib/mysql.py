from contextlib import contextmanager
import pymysql
from pymysql.cursors import DictCursor

from config import (
    USE_SSH_TUNNEL, SSH_HOST, SSH_PORT, SSH_USER, SSH_KEY_PATH,
    DB_HOST, DB_PORT, DB_USER, DB_PASSWORD
)
from lib.tunnel import ssh_tunnel

@contextmanager
def mysql_conn():
    if not USE_SSH_TUNNEL:
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            cursorclass=DictCursor,
            charset="utf8mb4",
            autocommit=True,
        )
        try:
            yield conn
        finally:
            conn.close()
        return

    if not (SSH_HOST and SSH_USER and SSH_KEY_PATH):
        raise ValueError("USE_SSH_TUNNEL=1 but SSH_HOST/SSH_USER/SSH_KEY_PATH not set")

    with ssh_tunnel(SSH_HOST, SSH_PORT, SSH_USER, SSH_KEY_PATH, DB_HOST, DB_PORT) as t:
        conn = pymysql.connect(
            host="127.0.0.1",
            port=t.local_bind_port,
            user=DB_USER,
            password=DB_PASSWORD,
            cursorclass=DictCursor,
            charset="utf8mb4",
            autocommit=True,
        )
        try:
            yield conn
        finally:
            conn.close()
