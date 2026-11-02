CREATE SCHEMA IF NOT EXISTS atlas;
CREATE SCHEMA IF NOT EXISTS sections;

CREATE TABLE atlas.municipalities (
    code text PRIMARY KEY CHECK (code ~ '^064[0-9]{3}$'),
    name text NOT NULL,
    province_code text NOT NULL CHECK (province_code = '064'),
    region_code text NOT NULL
);

CREATE TABLE atlas.datasets (
    id text PRIMARY KEY,
    metadata jsonb NOT NULL,
    status text NOT NULL CHECK (status IN ('ready', 'blocked')),
    verified_at text NOT NULL,
    position integer NOT NULL UNIQUE
);

CREATE TABLE atlas.indicators (
    id text PRIMARY KEY,
    dataset_id text NOT NULL REFERENCES atlas.datasets(id),
    label text NOT NULL,
    unit text NOT NULL,
    definition text NOT NULL,
    position integer NOT NULL UNIQUE
);

CREATE TABLE atlas.observations (
    municipality_code text NOT NULL REFERENCES atlas.municipalities(code),
    indicator_id text NOT NULL REFERENCES atlas.indicators(id),
    period text NOT NULL CHECK (period <> ''),
    value double precision,
    status text NOT NULL CHECK (status IN ('observed', 'missing', 'suppressed')),
    CHECK ((status = 'observed' AND value IS NOT NULL) OR
           (status <> 'observed' AND value IS NULL)),
    CHECK (value IS NULL OR (value > '-Infinity'::float8 AND value < 'Infinity'::float8)),
    PRIMARY KEY (municipality_code, indicator_id, period)
);
CREATE INDEX observation_period ON atlas.observations(indicator_id, period);

CREATE TABLE atlas.ingestion_runs (
    id text PRIMARY KEY,
    started_at text NOT NULL,
    completed_at text NOT NULL,
    mode text NOT NULL,
    report jsonb NOT NULL
);

CREATE TABLE atlas.categories (
    id text PRIMARY KEY,
    metadata jsonb NOT NULL,
    position integer NOT NULL UNIQUE
);

CREATE TABLE atlas.source_registry (
    id text PRIMARY KEY,
    category_id text NOT NULL REFERENCES atlas.categories(id),
    metadata jsonb NOT NULL,
    position integer NOT NULL UNIQUE
);

CREATE TABLE atlas.entities (
    dataset_id text NOT NULL REFERENCES atlas.datasets(id),
    source_id text NOT NULL,
    municipality_code text REFERENCES atlas.municipalities(code),
    title text NOT NULL,
    kind text NOT NULL,
    period text NOT NULL,
    payload jsonb NOT NULL,
    position integer NOT NULL UNIQUE,
    PRIMARY KEY (dataset_id, source_id)
);
CREATE INDEX entities_municipality ON atlas.entities(municipality_code, dataset_id);

CREATE TABLE atlas.dataset_imports (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dataset_key text NOT NULL,
    source_name text NOT NULL,
    source_url text,
    source_version text,
    reference_period text,
    published_at timestamptz,
    started_at timestamptz NOT NULL,
    completed_at timestamptz NOT NULL DEFAULT now(),
    imported_at timestamptz,
    records_processed integer NOT NULL DEFAULT 0 CHECK (records_processed >= 0),
    records_inserted integer NOT NULL DEFAULT 0 CHECK (records_inserted >= 0),
    records_updated integer NOT NULL DEFAULT 0 CHECK (records_updated >= 0),
    records_rejected integer NOT NULL DEFAULT 0 CHECK (records_rejected >= 0),
    status text NOT NULL CHECK (status IN ('success', 'failed', 'unchanged')),
    checksum text NOT NULL CHECK (checksum ~ '^[a-f0-9]{64}$'),
    error_message text,
    CHECK ((status = 'failed' AND error_message IS NOT NULL AND imported_at IS NULL) OR
           (status <> 'failed' AND error_message IS NULL AND imported_at IS NOT NULL))
);
CREATE INDEX dataset_imports_latest ON atlas.dataset_imports(dataset_key, id DESC);

CREATE TABLE atlas.publication_documents (
    key text PRIMARY KEY,
    document jsonb NOT NULL
);
CREATE TABLE atlas.publication_artifacts (
    path text PRIMARY KEY,
    payload bytea NOT NULL,
    sha256 text NOT NULL CHECK (sha256 ~ '^[a-f0-9]{64}$'),
    kind text NOT NULL
);

CREATE TABLE sections.municipalities (
    code text PRIMARY KEY CHECK (code ~ '^064[0-9]{3}$'),
    name text NOT NULL
);
CREATE TABLE sections.categories (
    id text PRIMARY KEY,
    metadata jsonb NOT NULL,
    position integer NOT NULL UNIQUE
);
CREATE TABLE sections.metrics (
    id text PRIMARY KEY,
    category text NOT NULL REFERENCES sections.categories(id),
    metadata jsonb NOT NULL,
    position integer NOT NULL UNIQUE
);
CREATE TABLE sections.values_annual (
    metric text NOT NULL REFERENCES sections.metrics(id),
    code text NOT NULL REFERENCES sections.municipalities(code),
    period text NOT NULL CHECK (period <> ''),
    value double precision,
    status text NOT NULL CHECK (status IN ('observed', 'missing', 'suppressed')),
    weight double precision,
    CHECK ((status = 'observed' AND value IS NOT NULL) OR
           (status <> 'observed' AND value IS NULL)),
    CHECK (value IS NULL OR (value > '-Infinity'::float8 AND value < 'Infinity'::float8)),
    CHECK (weight IS NULL OR (weight > '-Infinity'::float8 AND weight < 'Infinity'::float8)),
    PRIMARY KEY (metric, code, period)
);
CREATE INDEX annual_period ON sections.values_annual(metric, period);
CREATE TABLE sections.values_monthly (
    metric text NOT NULL REFERENCES sections.metrics(id),
    code text NOT NULL REFERENCES sections.municipalities(code),
    period text NOT NULL CHECK (period <> ''),
    value double precision,
    status text NOT NULL CHECK (status IN ('observed', 'missing', 'suppressed')),
    weight double precision,
    CHECK ((status = 'observed' AND value IS NOT NULL) OR
           (status <> 'observed' AND value IS NULL)),
    CHECK (value IS NULL OR (value > '-Infinity'::float8 AND value < 'Infinity'::float8)),
    CHECK (weight IS NULL OR (weight > '-Infinity'::float8 AND weight < 'Infinity'::float8)),
    PRIMARY KEY (metric, code, period)
);
CREATE INDEX monthly_period ON sections.values_monthly(metric, period);
CREATE TABLE sections.publication (
    metadata jsonb NOT NULL
);
