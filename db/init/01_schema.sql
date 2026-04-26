-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    -- =========================
    -- ORGANIZATIONS
    -- =========================
    CREATE TABLE organizations (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name VARCHAR(255) NOT NULL,
        status VARCHAR(50) DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- =========================
    -- USERS
    -- =========================
    CREATE TABLE users (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

        -- Auth
        email VARCHAR(255) UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        is_active BOOLEAN DEFAULT TRUE,

        -- User info
        user_name VARCHAR(100) NOT NULL,
        user_lastname VARCHAR(100) NOT NULL,

        -- Audit
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by UUID,

        modified_at TIMESTAMP,
        modified_by UUID,

        -- Foreign keys (opcional pero recomendado)
        CONSTRAINT fk_users_created_by FOREIGN KEY (created_by) REFERENCES users(id),
        CONSTRAINT fk_users_modified_by FOREIGN KEY (modified_by) REFERENCES users(id)
    );

    -- =========================
    -- ROLES
    -- =========================
    CREATE TABLE roles (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name VARCHAR(50) UNIQUE NOT NULL,
        description TEXT
    );

    -- =========================
    -- ORGANIZATION USERS (RBAC)
    -- =========================
    CREATE TABLE organization_users (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID REFERENCES users(id) ON DELETE CASCADE,
        organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
        role_id UUID REFERENCES roles(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, organization_id)
    );

    CREATE TABLE organization_profiles (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        organization_id UUID UNIQUE REFERENCES organizations(id) ON DELETE CASCADE,

        itin VARCHAR(50),

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP
    );

    CREATE TABLE organization_contacts (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,

        contact_name VARCHAR(255),
        contact_lastname VARCHAR(255),
        contact_title VARCHAR(255),

        contact_email VARCHAR(255),
        contact_phone VARCHAR(50),
        contact_mobile VARCHAR(50),

        is_primary BOOLEAN DEFAULT TRUE,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP
    );

-- =========================
-- SERVICES
-- =========================
CREATE TABLE services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- SERVICE ACTIVITIES
-- =========================
CREATE TABLE service_activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_id UUID REFERENCES services(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- INVOICES
-- =========================
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    amount NUMERIC(10,2) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    due_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- PAYMENTS
-- =========================
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_id UUID REFERENCES invoices(id) ON DELETE CASCADE,
    amount NUMERIC(10,2) NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    method VARCHAR(50)
);

-- =========================
-- SUPPORT TICKETS
-- =========================
CREATE TABLE tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ref VARCHAR(20) UNIQUE,

    organization_id UUID NOT NULL,

    subject VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'open',
    priority VARCHAR(20) DEFAULT 'medium',

    assignee VARCHAR(100) DEFAULT 'Unassigned',

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- =========================
-- TICKET MESSAGES
-- =========================
CREATE TABLE ticket_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    ticket_id UUID NOT NULL,

    sender VARCHAR(100),
    text TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT NOW()
);

-- =========================
-- ORGANIZATION INVITES
-- =========================
CREATE TABLE organization_invites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL,
    token VARCHAR(255) NOT NULL,
    organization_id UUID,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE invitation_tokens (
    id UUID PRIMARY KEY,
    email TEXT,
    organization_id UUID,
    token TEXT,
    expires_at TIMESTAMP
);


CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active',
    start_date DATE,
    due_date DATE,
    organization_id UUID NOT NULL
);

CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'todo',
    assignee VARCHAR(255),
    due_date DATE,
    project_id UUID NOT NULL,

    CONSTRAINT fk_project
        FOREIGN KEY (project_id)
        REFERENCES projects(id)
        ON DELETE CASCADE
);

