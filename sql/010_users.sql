CREATE TABLE IF NOT EXISTS warehouse.users
(
  id Int64,
  uuid String,
  email String,
  lms_user_id String,
  organization_id UInt64,
  login_at DateTime,
  role String
)
ENGINE = MergeTree
ORDER BY (organization_id, login_at, id);
