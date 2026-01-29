import os
from dotenv import load_dotenv
from sshtunnel import SSHTunnelForwarder
import pymysql
import clickhouse_connect

load_dotenv()

USE_SSH = os.getenv("USE_SSH_TUNNEL", "0") == "1"

def test_mysql_connection():
    print("🔌 Testando conexão MySQL...")

    db_user = os.environ["DB_USER"]
    db_password = os.environ["DB_PASSWORD"]
    db_host = os.environ["DB_HOST"]
    db_port = int(os.getenv("DB_PORT", "3306"))

    if not USE_SSH:
        conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            port=db_port,
        )
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            print("✅ MySQL direto OK:", cur.fetchone())
        conn.close()
        return

    print("🔐 Usando túnel SSH...")

    ssh_host = os.environ["SSH_HOST"]
    ssh_port = int(os.getenv("SSH_PORT", "22"))
    ssh_user = os.environ["SSH_USER"]
    ssh_key = os.environ["SSH_KEY_PATH"]

    with SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_username=ssh_user,
        ssh_pkey=ssh_key,
        remote_bind_address=(db_host, db_port),
        local_bind_address=("127.0.0.1", 0),
    ) as tunnel:
        conn = pymysql.connect(
            host="127.0.0.1",
            port=tunnel.local_bind_port,
            user=db_user,
            password=db_password,
        )
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            print("✅ MySQL via SSH OK:", cur.fetchone())
        conn.close()
        
def test_clickhouse_connection():
    print("📦 Testando conexão ClickHouse...")

    ch_host = os.getenv("CH_HOST")
    if not ch_host:
        raise RuntimeError("CH_HOST não está definido. Dentro do container use CH_HOST=clickhouse")

    ch = clickhouse_connect.get_client(
        host=ch_host,
        port=int(os.getenv("CH_PORT", "8123")),
        username=os.getenv("CH_USER", "default"),
        password=os.getenv("CH_PASSWORD", ""),
        database=os.getenv("CH_DB", "warehouse"),
    )

    res = ch.query("SELECT 1").result_rows
    print("✅ ClickHouse OK:", res)
    ch.close()
    print("📦 Testando conexão ClickHouse...")

    ch = clickhouse_connect.get_client(
        host=os.getenv("CH_HOST", "localhost"),
        port=int(os.getenv("CH_PORT", "8123")),
        username=os.getenv("CH_USER", "default"),
        password=os.getenv("CH_PASSWORD", ""),
        database=os.getenv("CH_DB", "warehouse"),
    )

    res = ch.query("SELECT 1").result_rows
    print("✅ ClickHouse OK:", res)
    ch.close()

if __name__ == "__main__":
    test_mysql_connection()
    test_clickhouse_connection()
    print("🎉 Tudo certo!")
