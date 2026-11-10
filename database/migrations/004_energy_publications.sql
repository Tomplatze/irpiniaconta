-- Each import stores a complete revision of the provincial Terna series.
CREATE TABLE atlas.energy_publications (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    checksum text NOT NULL CHECK (checksum ~ '^[a-f0-9]{64}$'),
    document jsonb NOT NULL CHECK (jsonb_typeof(document) = 'object' AND document->>'version' = '1'),
    imported_at timestamptz NOT NULL DEFAULT now()
);
