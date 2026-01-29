CREATE TABLE IF NOT EXISTS warehouse.contracts
(
  customer_id UInt64,
  customer_name String,
  contract_start Date,
  contract_end Date,
  created_at DateTime,
  updated_at DateTime
)
ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (customer_id, contract_start, contract_end);
