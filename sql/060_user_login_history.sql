CREATE TABLE IF NOT EXISTS warehouse.user_login_history
(
    organization_id UInt64,
    user_id         Int64,
    uuid            String,
    login_at        DateTime,
    role            String
)
ENGINE = MergeTree
ORDER BY (organization_id, uuid, login_at);
