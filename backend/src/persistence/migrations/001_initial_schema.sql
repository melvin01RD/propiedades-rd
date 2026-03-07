-- ============================================================
-- EXTENSIONES
-- ============================================================
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- ENUMS
-- ============================================================
CREATE TYPE user_role AS ENUM ('agent', 'owner', 'admin');

CREATE TYPE property_type AS ENUM (
    'house',
    'apartment',
    'commercial',
    'villa'
);

CREATE TYPE operation_type AS ENUM ('sale', 'rent');

CREATE TYPE currency AS ENUM ('DOP', 'USD');

CREATE TYPE property_status AS ENUM (
    'draft',
    'active',
    'inactive',
    'sold',
    'rented'
);

-- ============================================================
-- USERS (tabla base)
-- ============================================================
CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role          user_role NOT NULL,
    is_active     BOOLEAN NOT NULL DEFAULT true,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- AGENTS
-- ============================================================
CREATE TABLE agents (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id        UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    first_name     VARCHAR(100) NOT NULL,
    last_name      VARCHAR(100) NOT NULL,
    phone          VARCHAR(20),
    license_number VARCHAR(50),
    agency_name    VARCHAR(150),
    bio            TEXT,
    avatar_url     VARCHAR(500),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- OWNERS
-- ============================================================
CREATE TABLE owners (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id    UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    first_name VARCHAR(100) NOT NULL,
    last_name  VARCHAR(100) NOT NULL,
    phone      VARCHAR(20),
    avatar_url VARCHAR(500),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- PROPERTIES
-- ============================================================
CREATE TABLE properties (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id       UUID REFERENCES agents(id) ON DELETE SET NULL,
    owner_id       UUID REFERENCES owners(id) ON DELETE SET NULL,
    title          VARCHAR(200) NOT NULL,
    description    TEXT,
    property_type  property_type NOT NULL,
    operation_type operation_type NOT NULL,
    price          NUMERIC(15, 2) NOT NULL,
    currency       currency NOT NULL DEFAULT 'USD',
    bedrooms       SMALLINT,
    bathrooms      SMALLINT,
    parking_spots  SMALLINT,
    area_m2        NUMERIC(10, 2),
    floors         SMALLINT,
    year_built     SMALLINT,
    country        VARCHAR(100) NOT NULL DEFAULT 'República Dominicana',
    province       VARCHAR(100) NOT NULL,
    city           VARCHAR(100) NOT NULL,
    sector         VARCHAR(100),
    address        VARCHAR(255),
    location       GEOMETRY(Point, 4326),
    status         property_status NOT NULL DEFAULT 'draft',
    is_featured    BOOLEAN NOT NULL DEFAULT false,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_single_publisher CHECK (
        (agent_id IS NOT NULL AND owner_id IS NULL) OR
        (agent_id IS NULL AND owner_id IS NOT NULL)
    )
);

-- ============================================================
-- PROPERTY IMAGES
-- ============================================================
CREATE TABLE property_images (
    id                   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id          UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    cloudinary_url       VARCHAR(500) NOT NULL,
    cloudinary_public_id VARCHAR(255) NOT NULL,
    is_cover             BOOLEAN NOT NULL DEFAULT false,
    sort_order           SMALLINT NOT NULL DEFAULT 0,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- FAVORITES
-- ============================================================
CREATE TABLE favorites (
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, property_id)
);

-- ============================================================
-- ALERTS
-- ============================================================
CREATE TABLE alerts (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id           UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name              VARCHAR(100),
    filters           JSONB NOT NULL,
    is_active         BOOLEAN NOT NULL DEFAULT true,
    last_triggered_at TIMESTAMPTZ,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- ÍNDICES
-- ============================================================
CREATE INDEX idx_properties_status        ON properties(status);
CREATE INDEX idx_properties_type          ON properties(property_type);
CREATE INDEX idx_properties_operation     ON properties(operation_type);
CREATE INDEX idx_properties_province_city ON properties(province, city);
CREATE INDEX idx_properties_price         ON properties(price);
CREATE INDEX idx_properties_agent         ON properties(agent_id);
CREATE INDEX idx_properties_owner         ON properties(owner_id);
CREATE INDEX idx_properties_location      ON properties USING GIST(location);
CREATE INDEX idx_property_images_property ON property_images(property_id);
CREATE INDEX idx_alerts_user_active       ON alerts(user_id) WHERE is_active = true;
