-- Initialize AgroMind database

-- Enable PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS uuid-ossp;

-- Farms table
CREATE TABLE IF NOT EXISTS farms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    area_acres DECIMAL(10, 2),
    crop_type VARCHAR(100),
    owner_id UUID,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, owner_id)
);

-- Fields table
CREATE TABLE IF NOT EXISTS fields (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    area_acres DECIMAL(10, 2),
    crop_variety VARCHAR(100),
    planting_date DATE,
    expected_harvest DATE,
    geometry GEOMETRY(Polygon, 4326),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(farm_id, name)
);

-- Create spatial index on fields
CREATE INDEX idx_fields_geometry ON fields USING GIST (geometry);

-- Zones table (management units within fields)
CREATE TABLE IF NOT EXISTS zones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    area_acres DECIMAL(10, 2),
    geometry GEOMETRY(Polygon, 4326),
    zone_type VARCHAR(50),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_zones_geometry ON zones USING GIST (geometry);

-- Assets table (robots, drones, sensors)
CREATE TABLE IF NOT EXISTS assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_id UUID NOT NULL REFERENCES farms(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    asset_type VARCHAR(50) NOT NULL, -- 'robot', 'drone', 'sensor', 'sprayer'
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    serial_number VARCHAR(255) UNIQUE,
    last_location GEOMETRY(Point, 4326),
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'inactive', 'maintenance'
    battery_level DECIMAL(5, 2),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Detections table (from vision system)
CREATE TABLE IF NOT EXISTS detections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    detection_type VARCHAR(50) NOT NULL, -- 'weed', 'pest', 'disease', 'crop'
    class_name VARCHAR(100),
    confidence DECIMAL(5, 4),
    location GEOMETRY(Point, 4326),
    image_url VARCHAR(512),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_detections_field ON detections(field_id);
CREATE INDEX idx_detections_created ON detections(created_at DESC);

-- Treatments table
CREATE TABLE IF NOT EXISTS treatments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    zone_id UUID REFERENCES zones(id),
    treatment_type VARCHAR(50) NOT NULL, -- 'chemical', 'biological', 'manual'
    product_name VARCHAR(255),
    application_rate DECIMAL(10, 4),
    application_area DECIMAL(10, 2),
    application_date TIMESTAMP,
    effectiveness DECIMAL(5, 4),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_treatments_field ON treatments(field_id);

-- Sensor readings table (stored in TimescaleDB)
-- This is created for reference; actual timeseries data goes to TimescaleDB
CREATE TABLE IF NOT EXISTS sensor_metadata (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    sensor_type VARCHAR(50) NOT NULL, -- 'soil', 'weather', 'canopy', 'thermal'
    field_id UUID REFERENCES fields(id),
    location GEOMETRY(Point, 4326),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    prediction_type VARCHAR(50) NOT NULL, -- 'disease', 'pest', 'yield', 'weather'
    probability DECIMAL(5, 4),
    prediction_date DATE,
    predicted_value VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_predictions_field ON predictions(field_id);
CREATE INDEX idx_predictions_type ON predictions(prediction_type);

-- Create indices for common queries
CREATE INDEX idx_farms_owner ON farms(owner_id);
CREATE INDEX idx_fields_farm ON fields(farm_id);
CREATE INDEX idx_zones_field ON zones(field_id);
CREATE INDEX idx_assets_farm ON assets(farm_id);
CREATE INDEX idx_sensor_metadata_asset ON sensor_metadata(asset_id);

-- Grant permissions
GRANT USAGE ON SCHEMA public TO agromind;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO agromind;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO agromind;
