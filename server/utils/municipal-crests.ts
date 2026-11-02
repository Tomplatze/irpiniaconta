import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import type { MunicipalCrestManifest } from '../../shared/municipalCrests';

export interface StoredCrest {
  code: string;
  name: string;
  page?: string;
  image?: string;
  file?: string;
  filename?: string;
  sha256?: string;
  kind?: 'official' | 'redrawn';
  artist?: string;
}

export type StoredCrestManifest = Omit<MunicipalCrestManifest, 'records'> & { records: StoredCrest[] };
export const crestDirectory = join(process.cwd(), 'data', 'municipal-crests');

/** Read optional acquired evidence without exposing local filesystem paths. */
export async function readCrestManifest(): Promise<StoredCrestManifest | null> {
  try {
    return JSON.parse(await readFile(join(crestDirectory, 'manifest.json'), 'utf8')) as StoredCrestManifest;
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') return null;
    throw error;
  }
}
