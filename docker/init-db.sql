-- Initialize database for Real-Time Satellite Streaming System
-- TimescaleDB extension for time-series data

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Satellite Telemetry Table (time-series)
CREATE TABLE IF NOT EXISTS satellite_telemetry (
    time TIMESTAMPTZ NOT NULL,
    satellite_id INTEGER NOT NULL,
    norad_id INTEGER,
    satellite_name VARCHAR(100),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    altitude_km DOUBLE PRECISION,
    velocity_km_s DOUBLE PRECISION,
    x_pos_km DOUBLE PRECISION,
    y_pos_km DOUBLE PRECISION,
    z_pos_km DOUBLE PRECISION,
    vx_km_s DOUBLE PRECISION,
    vy_km_s DOUBLE PRECISION,
    vz_km_s DOUBLE PRECISION,
    orbital_period_min DOUBLE PRECISION,
    inclination_deg DOUBLE PRECISION,
    eccentricity DOUBLE PRECISION,
    PRIMARY KEY (time, satellite_id)
);

-- Convert to hypertable (TimescaleDB time-series optimization)
SELECT create_hypertable('satellite_telemetry', 'time', if_not_exists => TRUE);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_satellite_id ON satellite_telemetry (satellite_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_norad_id ON satellite_telemetry (norad_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_altitude ON satellite_telemetry (altitude_km, time DESC);

-- Threat Events Table
CREATE TABLE IF NOT EXISTS threat_events (
    id SERIAL PRIMARY KEY,
    time TIMESTAMPTZ NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    satellite_id_1 INTEGER,
    satellite_id_2 INTEGER,
    distance_km DOUBLE PRECISION,
    collision_probability DOUBLE PRECISION,
    time_to_closest_approach_min DOUBLE PRECISION,
    description TEXT,
    metadata JSONB
);

-- Convert to hypertable
SELECT create_hypertable('threat_events', 'time', if_not_exists => TRUE);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_threat_time ON threat_events (time DESC);
CREATE INDEX IF NOT EXISTS idx_threat_severity ON threat_events (severity, time DESC);
CREATE INDEX IF NOT EXISTS idx_threat_type ON threat_events (event_type, time DESC);

-- Satellite Catalog Table (reference data)
CREATE TABLE IF NOT EXISTS satellite_catalog (
    satellite_id SERIAL PRIMARY KEY,
    norad_id INTEGER UNIQUE NOT NULL,
    satellite_name VARCHAR(100),
    country VARCHAR(50),
    launch_date DATE,
    satellite_type VARCHAR(50),
    status VARCHAR(20),
    tle_line1 TEXT,
    tle_line2 TEXT,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_catalog_norad ON satellite_catalog (norad_id);
CREATE INDEX IF NOT EXISTS idx_catalog_name ON satellite_catalog (satellite_name);

-- Anomaly Detection Table
CREATE TABLE IF NOT EXISTS anomaly_detections (
    id SERIAL PRIMARY KEY,
    time TIMESTAMPTZ NOT NULL,
    satellite_id INTEGER NOT NULL,
    anomaly_type VARCHAR(50) NOT NULL,
    anomaly_score DOUBLE PRECISION,
    confidence DOUBLE PRECISION,
    description TEXT,
    metadata JSONB
);

-- Convert to hypertable
SELECT create_hypertable('anomaly_detections', 'time', if_not_exists => TRUE);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_anomaly_time ON anomaly_detections (time DESC);
CREATE INDEX IF NOT EXISTS idx_anomaly_satellite ON anomaly_detections (satellite_id, time DESC);

-- System Metrics Table (for monitoring)
CREATE TABLE IF NOT EXISTS system_metrics (
    time TIMESTAMPTZ NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DOUBLE PRECISION,
    tags JSONB,
    PRIMARY KEY (time, metric_name)
);

-- Convert to hypertable
SELECT create_hypertable('system_metrics', 'time', if_not_exists => TRUE);

-- Data retention policy (keep 30 days of raw data)
SELECT add_retention_policy('satellite_telemetry', INTERVAL '30 days', if_not_exists => TRUE);
SELECT add_retention_policy('threat_events', INTERVAL '90 days', if_not_exists => TRUE);
SELECT add_retention_policy('anomaly_detections', INTERVAL '90 days', if_not_exists => TRUE);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO satellite_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO satellite_user;

-- Insert some sample satellite catalog data
INSERT INTO satellite_catalog (norad_id, satellite_name, country, satellite_type, status) VALUES
(25544, 'ISS (ZARYA)', 'US/RUS', 'SPACE STATION', 'ACTIVE'),
(48274, 'STARLINK-1600', 'US', 'COMMUNICATIONS', 'ACTIVE'),
(43013, 'FENGYUN 4A', 'PRC', 'WEATHER', 'ACTIVE'),
(37849, 'METOP-C', 'ESA', 'WEATHER', 'ACTIVE'),
(28654, 'GPS BIIA-28', 'US', 'NAVIGATION', 'ACTIVE')
ON CONFLICT (norad_id) DO NOTHING;

COMMIT;