import clickhouse_connect
from config import CH_HOST, CH_PORT, CH_USER, CH_PASSWORD, CH_DB

def ch_client():
    return clickhouse_connect.get_client(
        host=CH_HOST,
        port=CH_PORT,
        username=CH_USER,
        password=CH_PASSWORD,
        database=CH_DB,
    )
