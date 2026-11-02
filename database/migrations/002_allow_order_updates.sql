-- Ordering is explicit, but positions need not be unique while metadata is reordered.
ALTER TABLE atlas.datasets DROP CONSTRAINT datasets_position_key;
ALTER TABLE atlas.indicators DROP CONSTRAINT indicators_position_key;
ALTER TABLE atlas.categories DROP CONSTRAINT categories_position_key;
ALTER TABLE atlas.source_registry DROP CONSTRAINT source_registry_position_key;
ALTER TABLE atlas.entities DROP CONSTRAINT entities_position_key;
ALTER TABLE sections.categories DROP CONSTRAINT categories_position_key;
ALTER TABLE sections.metrics DROP CONSTRAINT metrics_position_key;
