from datetime import datetime

from config import FORCE_LAST_RUN_AT
from lib.clickhouse import ch_client


def get_watermark(job: str):
    ch = ch_client()

    res = ch.query(
        """
        SELECT last_run_at, last_id
        FROM warehouse.etl_watermark
        WHERE job = %(job)s
        """,
        parameters={"job": job},
    ).result_rows

    if not res:
        if FORCE_LAST_RUN_AT:
            return datetime.fromisoformat(FORCE_LAST_RUN_AT), 0
        return datetime(1970, 1, 1), 0

    last_run_at, last_id = res[0]

    if isinstance(last_run_at, str):
        last_run_at = datetime.fromisoformat(last_run_at)

    return last_run_at, int(last_id)


def set_watermark(job: str, last_run_at: datetime, last_id: int):
    ch = ch_client()
    ch.command(
        """
        INSERT INTO warehouse.etl_watermark (job, last_run_at, last_id, updated_at)
        VALUES (%(job)s, %(last_run_at)s, %(last_id)s, now())
        """,
        parameters={
            "job": job,
            "last_run_at": last_run_at,
            "last_id": last_id,
        },
    )
