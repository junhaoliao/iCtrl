-- Initialize PostgreSQL for iCtrl tests
-- This creates the schema that DBProfile expects

CREATE SCHEMA IF NOT EXISTS ictrl;

-- Note: The actual tables are created by SQLAlchemy's db.create_all()
-- This file just ensures the schema exists and sets up any test fixtures

-- Grant permissions
GRANT ALL ON SCHEMA ictrl TO postgres;
