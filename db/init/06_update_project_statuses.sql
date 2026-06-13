-- status column is VARCHAR(50), no enum type to alter.
-- Migrate any existing 'active' rows to 'planning'.
UPDATE projects SET status = 'planning' WHERE status = 'active';
