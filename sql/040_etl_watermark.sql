CREATE TABLE IF NOT EXISTS warehouse.etl_watermark
(
  job String,
  last_run_at DateTime,
  last_id UInt64,
  updated_at DateTime
)
ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (job);

INSERT INTO warehouse.etl_watermark (job, last_run_at, last_id, updated_at)
VALUES
  ('users', toDateTime('1970-01-01 00:00:00'), 0, now()),
  ('organizations', toDateTime('1970-01-01 00:00:00'), 0, now()),
  ('projects', toDateTime('1970-01-01 00:00:00'), 0, now());
