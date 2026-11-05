import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { gunzipSync } from 'node:zlib';
import { getStore } from '@netlify/blobs';
import type { PoolClient } from 'pg';
import type { TerritoryResponse } from '../../shared/sections';
import type { MunicipalRecord } from './municipal-records';

type Row = Record<string, unknown>;
interface Manifest { version: number; entries: Record<string, { bytes: number; sha256: string }> }
interface Part { id: string; series: unknown[]; demographic_flow?: unknown[]; historical?: unknown[]; breakdown?: Array<{id:string;series:unknown[];historical?:unknown[]}> }
interface TerritorySnapshot { version: number; generated_at: string; province: TerritoryResponse; municipal: Record<string, Part[]> }
interface RecordSnapshot { version: number; records: Record<string, Record<string, MunicipalRecord[]>> }
interface SourceSnapshot { version: number; observations: Row[]; entities: Row[]; metrics: Row[]; categories: Row[]; towns: Row[]; annual: Row[]; monthly: Row[]; publication: Row[] }
const cache = new Map<string, Promise<unknown>>();
const storeName = 'irpiniaconta-snapshot-20261105';
const prefix = '20261105-v2/';

/** Select the explicit emergency publication mode. */
export function useSnapshotPublication(): boolean { return useRuntimeConfig().publicationMode === 'snapshot'; }

async function readBytes(name: string): Promise<Buffer> {
  const directory = process.env.ATLAS_SNAPSHOT_DIRECTORY;
  if (directory) return readFile(`${directory}/${name === 'manifest.json' ? 'manifest-v2.json' : name}`);
  const value = await getStore({ name: storeName, consistency: 'strong' }).get(prefix + name, { type: 'arrayBuffer' });
  if (!value) throw createError({statusCode:503,statusMessage:'Snapshot publication unavailable.'});
  return Buffer.from(value);
}
async function manifest(): Promise<Manifest> {
  const data = JSON.parse((await readBytes('manifest.json')).toString('utf8')) as Manifest;
  if (data.version !== 2 || !data.entries) throw createError({statusCode:503,statusMessage:'Snapshot manifest invalid.'});
  return data;
}
/** Read and verify an immutable private publication object. */
export function snapshotObject<T>(name: string): Promise<T> {
  const existing = cache.get(name) as Promise<T> | undefined;
  if (existing) return existing;
  const pending = (async () => {
    const [metadata, bytes] = await Promise.all([manifest(), readBytes(name)]);
    const expected = metadata.entries[name];
    if (!expected || expected.bytes !== bytes.length || createHash('sha256').update(bytes).digest('hex') !== expected.sha256) {
      throw createError({statusCode:503,statusMessage:'Snapshot integrity check failed.'});
    }
    const raw = gunzipSync(bytes).toString('utf8');
    return (name === 'sitemap.gz' ? raw : JSON.parse(raw)) as T;
  })();
  cache.set(name,pending);
  pending.catch(() => { if (cache.get(name) === pending) cache.delete(name); });
  return pending;
}
/** Reconstruct one or several municipalities without duplicating distributions. */
export async function snapshotTerritory(codes: string[]): Promise<TerritoryResponse> {
  const data = await snapshotObject<TerritorySnapshot>('territory.json.gz');
  const output = structuredClone(data.province);
  if (!codes.length) return output;
  output.scopes = codes.map(code => {
    const town = output.municipalities.find(item => item.code === code);
    if (!town) throw createError({statusCode:404,statusMessage:'Unknown municipality'});
    return town;
  });
  for (const category of output.categories) for (const metric of category.metrics) {
    const matches = codes.map(code => data.municipal[code]?.find(item => item.id === metric.id));
    if (matches.some(item => !item)) throw createError({statusCode:503,statusMessage:'Snapshot metric unavailable.'});
    metric.series = matches.flatMap(item => item!.series) as typeof metric.series;
    if (metric.demographic_flow) metric.demographic_flow.series = matches.flatMap(item => item!.demographic_flow ?? []) as typeof metric.demographic_flow.series;
    if (metric.historical) metric.historical.series = matches.flatMap(item => item!.historical ?? []) as typeof metric.historical.series;
    for (const group of metric.breakdown ?? []) {
      const parts = matches.map(item => item!.breakdown?.find(part => part.id === group.metric.id));
      if (parts.some(item => !item)) throw createError({statusCode:503,statusMessage:'Snapshot breakdown unavailable.'});
      group.series = parts.flatMap(item => item!.series) as typeof group.series;
      if (group.historical) group.historical.series = parts.flatMap(item => item!.historical ?? []) as typeof group.historical.series;
    }
  }
  return output;
}
/** Retrieve only the selected municipal group from the private snapshot. */
export async function snapshotRecords(code: string, group: string): Promise<MunicipalRecord[]> {
  const data = await snapshotObject<RecordSnapshot>('records.json.gz');
  if (!Object.hasOwn(data.records,code) || !Object.hasOwn(data.records[code]!,group)) throw createError({statusCode:404,statusMessage:'Unknown record group or municipality'});
  return data.records[code]![group]!;
}
/** Supply the existing section calculation functions with immutable snapshot rows. */
export async function snapshotSectionsClient(): Promise<PoolClient> {
  const data = await snapshotObject<SourceSnapshot>('api-source.json.gz');
  return { async query(query: string, parameters: unknown[] = []) {
    let rows: Row[];
    if (query.startsWith('SELECT metadata::text AS metadata FROM metrics WHERE')) rows = data.metrics.filter(row => row.category === parameters[0]);
    else if (query.startsWith('SELECT metadata::text AS metadata FROM metrics ORDER')) rows = data.metrics;
    else if (query.startsWith('SELECT code,name FROM municipalities')) rows = data.towns;
    else if (query.startsWith('SELECT metadata::text AS metadata FROM categories')) rows = data.categories;
    else if (query.startsWith('SELECT metadata::text AS metadata FROM publication')) rows = data.publication;
    else if (query.includes('FROM values_annual WHERE metric=$1') || query.includes('FROM values_monthly WHERE metric=$1')) {
      const source = query.includes('values_monthly') ? data.monthly : data.annual;
      rows = source.filter(row => row.metric === parameters[0] && (parameters[1] == null || row.period === parameters[1]) && (parameters[2] == null || row.code === parameters[2]));
    } else throw createError({statusCode:503,statusMessage:'Unsupported snapshot query.'});
    return {rows,rowCount:rows.length};
  } } as unknown as PoolClient;
}
/** Read general source observations and entity rows for legacy public API compatibility. */
export function snapshotSource(): Promise<SourceSnapshot> { return snapshotObject<SourceSnapshot>('api-source.json.gz'); }
