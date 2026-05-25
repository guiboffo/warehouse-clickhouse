from datetime import datetime

from lib.mysql import mysql_conn
from lib.clickhouse import ch_client
from lib.watermark import get_watermark, set_watermark
from config import BATCH_SIZE

SQL_USERS = """
SELECT
  CAST(uo.id AS SIGNED)        AS id,
  u.id                         AS uuid,
  u.email                      AS email,
  COALESCE(ul.lms_user_id, '') AS lms_user_id,
  uo.organization_id           AS organization_id,
  uo.last_login_at             AS login_at,
  CASE
    WHEN EXISTS (
      SELECT 1
      FROM dreamshaper.cluster_administrator ca
      WHERE ca.user_id = u.id
    ) THEN 'Teacher'
    ELSE 'Student'
  END AS role
FROM dreamshaper.user_organization uo
JOIN dreamshaper.user u
  ON u.id = uo.user_id
JOIN dreamshaper.organization o
  ON uo.organization_id = o.id
LEFT JOIN auth_api.user u2
  ON u2.uuid = u.id
LEFT JOIN auth_api.user_lms ul
  ON ul.user_id = u2.user_id
 AND ul.lms_org_id = o.subdomain
WHERE
  (
    uo.last_login_at > %(last_run_at)s
    OR (uo.last_login_at = %(last_run_at)s AND uo.id > %(last_id)s)
  )
ORDER BY uo.last_login_at ASC, uo.id ASC
LIMIT %(limit)s
"""


def run_users() -> None:
    job = "users"
    last_run_at, last_id = get_watermark(job)

    print(f"[users] starting from last_run_at={last_run_at} last_id={last_id}")

    total = 0
    max_ts = last_run_at
    max_id = last_id

    ch = ch_client()
    try:
        while True:
            with mysql_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(SQL_USERS, {"last_run_at": last_run_at, "last_id": last_id, "limit": BATCH_SIZE})
                    rows = cur.fetchall()

            if not rows:
                break

            data = []
            history_data = []
            for r in rows:
                row = [
                    int(r["id"]),
                    str(r["uuid"]),
                    str(r["email"] or ""),
                    str(r["lms_user_id"] or ""),
                    int(r["organization_id"]),
                    r["login_at"],
                    str(r["role"] or ""),
                ]
                data.append(row)
                history_data.append([
                    int(r["organization_id"]),
                    int(r["id"]),
                    str(r["uuid"]),
                    r["login_at"],
                    str(r["role"] or ""),
                ])

            ch.insert(
                "warehouse.users",
                data,
                column_names=["id", "uuid", "email", "lms_user_id", "organization_id", "login_at", "role"],
            )
            ch.insert(
                "warehouse.user_login_history",
                history_data,
                column_names=["organization_id", "user_id", "uuid", "login_at", "role"],
            )

            total += len(rows)

            last_row = rows[-1]
            last_run_at = last_row["login_at"]
            last_id = int(last_row["id"])

            if last_run_at > max_ts or (last_run_at == max_ts and last_id > max_id):
                max_ts = last_run_at
                max_id = last_id

            print(f"[users] batch inserted={len(rows)} total={total} new_watermark=({last_run_at}, {last_id})")

        if total > 0:
            set_watermark(job, max_ts, max_id)
            print(f"[users] done total={total} watermark set to ({max_ts}, {max_id})")
        else:
            print("[users] done no new rows")
    finally:
        ch.close()
