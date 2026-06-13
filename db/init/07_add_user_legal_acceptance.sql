CREATE TABLE IF NOT EXISTS user_legal_acceptances (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id   UUID NOT NULL REFERENCES organizations(id),
    user_id           UUID NOT NULL REFERENCES users(id),
    document_type     VARCHAR(50) NOT NULL,
    document_version  VARCHAR(20) NOT NULL,
    accepted_at       TIMESTAMP NOT NULL DEFAULT NOW(),
    ip_address        VARCHAR(45),
    user_agent        TEXT
);

CREATE INDEX IF NOT EXISTS idx_legal_acceptance_user    ON user_legal_acceptances(user_id);
CREATE INDEX IF NOT EXISTS idx_legal_acceptance_org     ON user_legal_acceptances(organization_id);
CREATE INDEX IF NOT EXISTS idx_legal_acceptance_type    ON user_legal_acceptances(document_type, document_version);
