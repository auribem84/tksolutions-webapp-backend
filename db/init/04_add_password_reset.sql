-- Password reset token fields for users table
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS reset_token VARCHAR(255),
    ADD COLUMN IF NOT EXISTS reset_token_expires_at TIMESTAMP;
