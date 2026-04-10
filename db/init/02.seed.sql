INSERT INTO roles (name, description) VALUES
('admin', 'Full access to organization'),
('manager', 'Manage services and users'),
('viewer', 'Read-only access')
ON CONFLICT (name) DO NOTHING;