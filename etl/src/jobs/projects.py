from datetime import datetime, timezone, timedelta

from lib.mysql import mysql_conn
from lib.clickhouse import ch_client
from lib.watermark import get_watermark, set_watermark
from config import BATCH_SIZE, PROJECTS_LAG_MINUTES


SQL_PROJECTS = """
SELECT
  p.organization_id                        AS organization_id,
  p.id                                     AS project_id,
  p.percentage                             AS percentage,
  m.user_id                                AS uuid,
  m.status                                 AS status,
  p.updated_at                             AS p_updated_at,
  m.updated_at                             AS m_updated_at,
  GREATEST(p.updated_at, m.updated_at)     AS wm_ts,
  CAST(CONV(SUBSTR(MD5(CONCAT(p.id, '|', m.user_id)), 1, 16), 16, 10) AS UNSIGNED) AS row_key
FROM dreamshaper.project p
JOIN dreamshaper.membership m
  ON m.project_id = p.id
WHERE p.deleted_at IS NULL
  -- 🔒 Cutoff fixo por execução para o job terminar
  AND GREATEST(p.updated_at, m.updated_at) <= %(cutoff_ts)s
  AND (
    GREATEST(p.updated_at, m.updated_at) > %(last_run_at)s
    OR (
      GREATEST(p.updated_at, m.updated_at) = %(last_run_at)s
      AND CAST(CONV(SUBSTR(MD5(CONCAT(p.id, '|', m.user_id)), 1, 16), 16, 10) AS UNSIGNED) > %(last_id)s
    )
  )
ORDER BY wm_ts ASC, row_key ASC
LIMIT %(limit)s
"""


def run_projects() -> None:
    job = "projects"
    last_run_at, last_id = get_watermark(job)

    # Cutoff fixo: "até agora - lag"
    cutoff_ts = datetime.now(timezone.utc) - timedelta(minutes=PROJECTS_LAG_MINUTES)

    print(f"[projects] starting from last_run_at={last_run_at} last_id={last_id}")
    print(f"[projects] cutoff_ts={cutoff_ts.isoformat()} (lag={PROJECTS_LAG_MINUTES}m)")

    total = 0
    max_ts = last_run_at
    max_id = last_id

    ch = ch_client()
    try:
        while True:
            with mysql_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        SQL_PROJECTS,
                        {
                            "last_run_at": last_run_at,
                            "last_id": last_id,
                            "cutoff_ts": cutoff_ts,
                            "limit": BATCH_SIZE,
                        },
                    )
                    rows = cur.fetchall()

            if not rows:
                break

            data = []
            for r in rows:
                data.append([
                    int(r["organization_id"]),
                    int(r["project_id"]),
                    float(r["percentage"] or 0),
                    str(r["uuid"]),
                    str(r["status"] or ""),
                    r["p_updated_at"],
                    r["m_updated_at"],
                ])

            ch.insert(
                "warehouse.projects",
                data,
                column_names=[
                    "organization_id",
                    "project_id",
                    "percentage",
                    "uuid",
                    "status",
                    "p_updated_at",
                    "m_updated_at",
                ],
            )

            total += len(rows)

            # Avança cursor para o último registro do lote (já ordenado)
            last_row = rows[-1]
            last_run_at = last_row["wm_ts"]
            last_id = int(last_row["row_key"])

            # Guarda watermark máximo da execução
            if last_run_at > max_ts or (last_run_at == max_ts and last_id > max_id):
                max_ts = last_run_at
                max_id = last_id

            print(f"[projects] batch inserted={len(rows)} total={total} new_watermark=({last_run_at}, {last_id})")

        if total > 0:
            set_watermark(job, max_ts, max_id)
            print(f"[projects] done total={total} watermark set to ({max_ts}, {max_id})")
        else:
            print("[projects] done no new rows")
    finally:
        ch.close()
