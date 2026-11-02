import { createHash } from 'node:crypto';
import { gunzip } from 'node:zlib';
import { promisify } from 'node:util';
import type { PoolClient } from 'pg';
import { readCollection } from './collection';
import { readScope, entityRecord } from './scope';
import type { EntityRecord } from '../../shared/catalogue';

export interface MunicipalRecord {
  id: string; title: string; period: string; publisher: string; sourceTitle: string; sourceUrl: string;
  fields: Array<{ label: string; value: string }>;
}
export interface MunicipalRecordPage { total: number; records: MunicipalRecord[]; offset: number; limit: number }

const groups: Record<string, { entities?: string[]; collected?: string }> = {
  schools: { entities: ['mim_schools'] }, pharmacies: { entities: ['health_pharmacies'] },
  authority: { entities: ['ipa_entities'] }, digital: { entities: ['pa_digitale'] },
  libraries: { entities: ['province_libraries'] },
  heritage: { entities: ['province_castles', 'province_religious', 'province_archaeology', 'province_palaces'] },
  province_schools: { entities: ['province_schools'] },
  works: { entities: ['province_works'] },
  pnrr: { collected: 'pnrr-projects-20260613' }, cohesion: { collected: 'opencoesione-campania-20260630' },
  fortified: { collected: 'siat-cultural-layer-2' }, historic: { collected: 'siat-cultural-layer-8' },
  cultural: { collected: 'mic-cultural-places-campania' },
};
const fieldLabels: Record<string, string> = {
  indirizzo: 'Indirizzo', Indirizzo: 'Indirizzo', INDIRIZZOSCUOLA: 'Indirizzo',
  DESCRIZIONETIPOLOGIAGRADOISTRUZIONESCUOLA: 'Ordine di scuola', CODICESCUOLA: 'Codice scuola',
  CODICEISTITUTORIFERIMENTO: 'Istituto di riferimento', ANNOSCOLASTICO: 'Anno scolastico',
  descrizione_tipologia: 'Tipologia', cod_farmacia: 'Codice farmacia', localizzazione: 'Sede',
  data_inizio_validita: 'Valida dal', data_fine_validita: 'Valida fino al',
  Codice_IPA: 'Codice IPA', Codice_Categoria: 'Codice categoria', codice_ipa: 'Codice IPA', Tipologia: 'Tipologia', Data_aggiornamento: 'Aggiornamento fonte',
  codice_cup: 'CUP', amount_eur: 'Importo assegnato', stato_candidatura: 'Stato nella fonte',
  data_finanziamento: 'Data finanziamento', decreto_finanziamento: 'Decreto', data_stato_candidatura: 'Data stato',
  'Telefono': 'Telefono', 'Telefono 1': 'Telefono', 'Telefono 2': 'Telefono', 'Email': 'Email', 'E-mail': 'Email', 'e-mail': 'Email', 'pec': 'PEC',
  'PEC': 'PEC', 'Sito Web': 'Sito web', 'Sito web': 'Sito web', 'Descrizione': 'Descrizione',
  'Codice Meccanografico': 'Codice scuola', 'Tipologia scuola': 'Tipologia', 'Denominazione Istituto': 'Istituto di riferimento', 'Scuola': 'Tipologia', 'Distretto': 'Distretto', 'ISIL': 'Codice ISIL',
};
const collectedFields: Record<string, Record<string, string>> = {
  pnrr: { 'Titolo Progetto': 'Titolo originale del progetto', 'CUP': 'CUP', 'Codice Locale Progetto': 'Codice progetto', 'Sintesi Progetto': 'Descrizione', 'Stato Avanzamento Progetto': 'Stato progetto', 'Finanziamento Totale': 'Finanziamento totale', 'Soggetto Attuatore': 'Soggetto attuatore', 'Data Inizio Progetto Effettiva': 'Inizio effettivo', 'Data Fine Progetto Prevista': 'Fine prevista', 'Data Fine Progetto Effettiva': 'Fine effettiva', 'Descrizione Misura': 'Misura' },
  cohesion: { 'COD_LOCALE_PROGETTO': 'Codice progetto', 'CUP': 'CUP', 'OC_SINTESI_PROGETTO': 'Descrizione', 'OC_TEMA_SINTETICO': 'Tema', 'OC_DESCR_CICLO': 'Programmazione', 'FINANZ_TOTALE_PUBBLICO': 'Finanziamento pubblico', 'OC_STATO_PROGETTO': 'Stato progetto', 'DATA_AGGIORNAMENTO': 'Aggiornamento fonte', 'OC_LINK': 'Scheda OpenCoesione' },
  fortified: { Località: 'Località', Stato_Attu: 'Stato', Fruibilità: 'Fruibilità', Rudere: 'Rudere', Scomparso: 'Scomparso' },
  historic: { PIANO_RECU: 'Piano di recupero', NOT_INT: 'Note' },
  cultural: { 'dc:type': 'Tipologia', 'l0:description': 'Descrizione' },
};
interface SourceRow { municipality_codes: string[]; period: string; source: Record<string, unknown> }
const decompress = promisify(gunzip);
const cache = new Map<string, Promise<Map<string, MunicipalRecord[]>>>();
function textValue(value: unknown): string | null {
  if (typeof value === 'number' && Number.isFinite(value)) return String(value);
  if (typeof value === 'string') {
    const result = value.trim();
    return result && !['-', 'non disponibile', 'n.d.', 'null'].includes(result.toLowerCase()) ? result : null;
  }
  if (value && typeof value === 'object' && !Array.isArray(value)) return textValue((value as Record<string, unknown>)['@value']);
  return null;
}
function fields(source: Record<string, unknown>, labels: Record<string, string>): MunicipalRecord['fields'] {
  return Object.entries(labels).flatMap(([key,label]) => {
    let value = textValue(source[key]);
    if (!value) return [];
    if (key === 'ANNOSCOLASTICO' && /^\d{6}$/.test(value)) value = `${value.slice(0,4)}/${value.slice(0,2)}${value.slice(4)}`;
    if (key === 'amount_eur' && typeof source[key] === 'number') value = new Intl.NumberFormat('it-IT', { style:'currency', currency:'EUR' }).format(source[key]);
    if (key === 'Finanziamento Totale' && /^-?\d+(?:\.\d+)?$/.test(value)) value = new Intl.NumberFormat('it-IT', { style:'currency', currency:'EUR' }).format(Number(value));
    if (key === 'FINANZ_TOTALE_PUBBLICO' && /^-?\d+(?:,\d+)?$/.test(value)) value = new Intl.NumberFormat('it-IT', { style:'currency', currency:'EUR' }).format(Number(value.replace(',','.')));
    return [{label,value}];
  });
}
function fromEntity(record: EntityRecord, sources: Map<string, { publisher: string; title: string; landing_url: string }>): MunicipalRecord {
  const source = sources.get(record.dataset_id);
  return { id:`${record.dataset_id}:${record.source_id}`, title:record.title, period:record.period,
    publisher:source?.publisher ?? '', sourceTitle:source?.title ?? record.dataset_id, sourceUrl:source?.landing_url ?? '',
    fields:fields(record.payload,fieldLabels) };
}
/** Project source fields without joining records from different catalogues. */
function fromCollected(row: SourceRow, group: string, metadata: { title: string; publisher: string; url: string }): MunicipalRecord {
  const root = row.source;
  const source = group === 'fortified' || group === 'historic' ? root.properties as Record<string,unknown> : group === 'cultural' ? root.place as Record<string,unknown> : root;
  const title = (group==='pnrr' ? textValue(source['Titolo Procedura']) : null) ?? textValue(source[group==='pnrr' ? 'Titolo Progetto' : group==='cohesion' ? 'OC_TITOLO_PROGETTO' : group==='fortified' ? 'Immobile' : group==='historic' ? 'DENOMINAZI' : 'cis:institutionalCISName']) ?? 'Denominazione non disponibile';
  const id = group==='pnrr' ? `${source.CUP}:${source['Codice Locale Progetto']}` : group==='cohesion' ? String(source.COD_LOCALE_PROGETTO) : group==='cultural' ? String(source['@id']) : String(source.OBJECTID);
  return {id:`${group}:${id}`,title,period:row.period,publisher:metadata.publisher,sourceTitle:metadata.title,sourceUrl:metadata.url,fields:fields(source,collectedFields[group] ?? {})};
}
/** Read checksummed published artifacts once and retain only display fields, grouped by ISTAT code. */
async function collectedRecords(database: PoolClient, id: string, group: string): Promise<Map<string, MunicipalRecord[]>> {
  const inventory = await readCollection(database);
  const dataset = inventory.datasets.find(item => item.id === id);
  if (!dataset) throw createError({statusCode:503,statusMessage:'Collected records unavailable'});
  const key = `${group}:${dataset.staging_sha256}`;
  let pending = cache.get(key);
  if (!pending) {
    const result = await database.query<{payload:Buffer;sha256:string}>('SELECT payload,sha256 FROM atlas.publication_artifacts WHERE path=$1 AND kind=$2',[dataset.staging_file,'source-rows']);
    const artifact = result.rows[0];
    if (!artifact || artifact.sha256 !== dataset.staging_sha256 || createHash('sha256').update(artifact.payload).digest('hex') !== dataset.staging_sha256) throw createError({statusCode:503,statusMessage:'Collected records failed verification'});
    const metadata = {title:dataset.title,publisher:dataset.publisher,url:dataset.source_urls[0] ?? ''};
    pending = decompress(artifact.payload).then(buffer => {
      const towns = new Map<string,Map<string,MunicipalRecord>>();
      for (const line of buffer.toString('utf8').split('\n')) if (line) {
        const row = JSON.parse(line) as SourceRow;
        const record = fromCollected(row,group,metadata);
        for (const code of row.municipality_codes) {
          const bucket = towns.get(code) ?? new Map<string,MunicipalRecord>();
          if (!bucket.has(record.id)) bucket.set(record.id,record);
          towns.set(code,bucket);
        }
      }
      return new Map([...towns].map(([code,bucket])=>[code,[...bucket.values()].sort((a,b)=>a.title.localeCompare(b.title,'it'))]));
    });
    cache.set(key,pending);
    pending.catch(() => { if (cache.get(key)===pending) cache.delete(key); });
  }
  return pending;
}
/** Resolve only records belonging to one verified municipality and editorial group. */
export async function loadMunicipalRecords(database: PoolClient, code: string, group: string): Promise<MunicipalRecord[]> {
  const definition = groups[group];
  if (!Object.hasOwn(groups,group) || !definition) throw createError({statusCode:404,statusMessage:'Unknown record group'});
  const municipality = await database.query('SELECT code FROM municipalities WHERE code=$1',[code]);
  if (!municipality.rowCount) throw createError({statusCode:404,statusMessage:'Unknown municipality'});
  let records: MunicipalRecord[];
  if (definition.entities) {
    const scope = await readScope(database);
    const sources = new Map(scope.sources.filter(item => item.dataset_id).map(item => [item.dataset_id!,item]));
    const result = await database.query<Record<string,unknown>>(`SELECT e.dataset_id,e.source_id,e.municipality_code,e.title,e.kind,e.period,e.payload::text AS payload,m.name AS municipality_name FROM entities e JOIN municipalities m ON m.code=e.municipality_code WHERE e.municipality_code=$1 AND e.dataset_id=ANY($2::text[]) ORDER BY lower(e.title),e.title,e.source_id`,[code,definition.entities]);
    records = result.rows.map(entityRecord).filter(row => group!=='schools' || row.payload.SEDESCOLASTICA==='SI').map(row=>fromEntity(row,sources));
  } else {
    const towns = await collectedRecords(database,definition.collected!,group);
    records = towns.get(code) ?? [];
  }
  return records;
}

/** Keep the existing bounded endpoint available to other consumers. */
export async function municipalRecords(database: PoolClient, code: string, group: string, offset: number, limit: number): Promise<MunicipalRecordPage> {
  const records = await loadMunicipalRecords(database,code,group);
  return {total:records.length,records:records.slice(offset,offset+limit),offset,limit};
}
