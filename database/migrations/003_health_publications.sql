-- Health publications contain only reviewed, province-wide or whole-ASL aggregates.
-- Keep revisions append-only so a failed or partial import never replaces the last release.
CREATE TABLE atlas.health_publications (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    checksum text NOT NULL CHECK (checksum ~ '^[a-f0-9]{64}$'),
    document jsonb NOT NULL CHECK (jsonb_typeof(document) = 'object' AND document->>'version' = '1'),
    imported_at timestamptz NOT NULL DEFAULT now()
);
