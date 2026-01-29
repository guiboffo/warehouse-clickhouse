CREATE TABLE IF NOT EXISTS warehouse.organizations
(
  organization_id UInt64,
  organization_subdomain String,
  lms_integration UInt8,
  customer_id UInt64,
  customer_name String,
  root_customer_id UInt64,
  root_costumer_name String,
  created_at DateTime,
  updated_at DateTime
)
ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (organization_id);
