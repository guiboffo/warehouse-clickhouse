from lib.mysql import mysql_conn
from lib.clickhouse import ch_client

SQL_ORGS_FULL = """
WITH RECURSIVE customer_tree AS (
  SELECT
    o.id AS organization_id,
    o.subdomain AS organization_subdomain,
    o.lms_integration,
    o.created_at,
    o.updated_at,
    o.customer_id,
    oc.id        AS current_customer_id,
    oc.parent_id,
    oc.name      AS current_customer_name
  FROM dreamshaper.organization o
  LEFT JOIN dreamshaper.organization_customer oc
    ON oc.id = o.customer_id

  UNION ALL

  SELECT
    ct.organization_id,
    ct.organization_subdomain,
    ct.lms_integration,
    ct.created_at,
    ct.updated_at,
    ct.customer_id,
    parent.id,
    parent.parent_id,
    parent.name
  FROM customer_tree ct
  JOIN dreamshaper.organization_customer parent
    ON parent.id = ct.parent_id
)

SELECT
  ct.organization_id,
  ct.organization_subdomain,
  ct.lms_integration,
  ct.created_at,
  ct.updated_at,
  ct.customer_id,
  direct.name              AS customer_name,
  ct.current_customer_id   AS root_customer_id,
  ct.current_customer_name AS root_costumer_name
FROM customer_tree ct
LEFT JOIN dreamshaper.organization_customer direct
  ON direct.id = ct.customer_id
WHERE ct.parent_id IS NULL
"""


def run_organizations() -> None:
    """
    Full refresh diário da dimensão organizations.

    Estratégia:
    - Busca o estado atual completo no MySQL
    - Insere tudo no ClickHouse (append)
    - ClickHouse consolida "estado atual" via ReplacingMergeTree(updated_at)
      (ou via view organizations_current com argMax)
    """
    print("[organizations] full refresh starting")

    ch = ch_client()
    try:
        with mysql_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(SQL_ORGS_FULL)
                rows = cur.fetchall()

        if not rows:
            print("[organizations] done no rows returned")
            return

        data = []
        for r in rows:
            data.append([
                int(r["organization_id"]),
                str(r["organization_subdomain"] or ""),
                int(r["lms_integration"] or 0),
                int(r["customer_id"] or 0),
                str(r["customer_name"] or ""),
                int(r["root_customer_id"] or 0),
                str(r["root_costumer_name"] or ""),
                r["created_at"],
                r["updated_at"],
            ])

        ch.insert(
            "warehouse.organizations",
            data,
            column_names=[
                "organization_id",
                "organization_subdomain",
                "lms_integration",
                "customer_id",
                "customer_name",
                "root_customer_id",
                "root_costumer_name",
                "created_at",
                "updated_at",
            ],
        )

        print(f"[organizations] done full refresh inserted={len(rows)}")
    finally:
        ch.close()
