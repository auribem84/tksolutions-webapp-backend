-- Add new project status values to the existing enum
ALTER TYPE projectstatus ADD VALUE IF NOT EXISTS 'planning';
ALTER TYPE projectstatus ADD VALUE IF NOT EXISTS 'in_progress';
ALTER TYPE projectstatus ADD VALUE IF NOT EXISTS 'in_review';
ALTER TYPE projectstatus ADD VALUE IF NOT EXISTS 'support';
ALTER TYPE projectstatus ADD VALUE IF NOT EXISTS 'cancelled';

-- Migrate existing 'active' records to 'planning'
UPDATE projects SET status = 'planning' WHERE status = 'active';
