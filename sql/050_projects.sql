CREATE TABLE IF NOT EXISTS warehouse.projects
(
  organization_id UInt64,
  project_id UInt64,
  percentage Float64,
  uuid String,
  status String,
  p_updated_at DateTime,
  m_updated_at DateTime,
  version_ts DateTime
)
ENGINE = MergeTree
ORDER BY (project_id, uuid, version_ts);
