CREATE TABLE IF NOT EXISTS warehouse.projects
(
    organization_id UInt64,
    project_id      UInt64,
    percentage      Float32,
    uuid            String,
    status          String,
    p_updated_at    DateTime,
    m_updated_at    DateTime,
    version_ts      DateTime,
    INDEX idx_uuid uuid TYPE bloom_filter(0.01) GRANULARITY 4
)
ENGINE = ReplacingMergeTree(version_ts)
ORDER BY (organization_id, project_id, uuid)
SETTINGS index_granularity = 8192;
