CREATE TABLE IF NOT EXISTS warehouse.project_progress_history
(
    organization_id UInt64,
    project_id      UInt64,
    uuid            String,
    percentage      Float32,
    status          String,
    p_updated_at    DateTime,
    m_updated_at    DateTime,
    version_ts      DateTime
)
ENGINE = MergeTree
ORDER BY (organization_id, project_id, uuid, version_ts);
