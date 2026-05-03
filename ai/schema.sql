-- 가게 마스터 테이블 (안정 필드만)
CREATE TABLE IF NOT EXISTS places (
    place_id            VARCHAR(20) PRIMARY KEY,
    name                TEXT NOT NULL,
    category            TEXT,
    category_group_code VARCHAR(10),
    phone               TEXT,
    address_name        TEXT,
    road_address_name   TEXT,
    lat                 DOUBLE PRECISION,
    lng                 DOUBLE PRECISION,
    place_url           TEXT,
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_places_category ON places(category_group_code);
CREATE INDEX IF NOT EXISTS idx_places_coords   ON places(lat, lng);