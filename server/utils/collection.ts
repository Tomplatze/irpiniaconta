import type { PoolClient } from 'pg';
import type { CollectionInventory } from '../../shared/collection';

/** Read a validated publication document through the request's consistent database snapshot. */
export async function readPublicationDocument<T>(database: PoolClient, key: 'collection-inventory' | 'sections-map' | 'editorial'): Promise<T> {
  const result = await database.query<{ document: T }>('SELECT document FROM atlas.publication_documents WHERE key = $1', [key]);
  const document = result.rows[0]?.document;
  if (!document) throw createError({ statusCode: 503, statusMessage: 'Publication assets unavailable. Import the publication assets.' });
  return document;
}

/** Read collected-source metadata independently of the selected public indicators. */
export async function readCollection(database: PoolClient): Promise<CollectionInventory> {
  const inventory = await readPublicationDocument<CollectionInventory>(database, 'collection-inventory');
  if (inventory.schema_version !== 1 || !Array.isArray(inventory.sources) || !Array.isArray(inventory.datasets)) {
    throw createError({ statusCode: 503, statusMessage: 'Collection inventory schema invalid.' });
  }
  return inventory;
}
