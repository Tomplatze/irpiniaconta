import { withDatabase } from '../utils/database';
import { loadMunicipalRecords, municipalRecords } from '../utils/municipal-records';

/** Provide a lightweight title index or one record, scoped to a verified municipality. */
export default defineEventHandler(event => {
  const query = getQuery(event);
  const code = query.code;
  const group = query.group;
  const offset = query.offset === undefined ? 0 : Number(query.offset);
  const limit = query.limit === undefined ? 8 : Number(query.limit);
  if (typeof code !== 'string' || !/^064\d{3}$/.test(code) || typeof group !== 'string' || !Number.isInteger(offset) || offset < 0 || !Number.isInteger(limit) || limit < 1 || limit > 30 || (query.view !== undefined && query.view !== 'index') || (query.id !== undefined && (typeof query.id !== 'string' || !query.id || query.id.length > 512)) || (query.view !== undefined && query.id !== undefined)) throw createError({statusCode:400,statusMessage:'Invalid municipal record request'});
  return withDatabase(async database => {
    if (query.view === 'index') {
      const records = await loadMunicipalRecords(database,code,group);
      return {total:records.length,records:records.map(({id,title,fields})=>({id,title,reference:fields.find(field=>field.label==='CUP' || field.label==='Codice scuola')?.value}))};
    }
    if (typeof query.id === 'string') {
      const records = await loadMunicipalRecords(database,code,group);
      const record = records.find(item=>item.id===query.id);
      if (!record) throw createError({statusCode:404,statusMessage:'Record not found for this municipality'});
      return record;
    }
    return municipalRecords(database,code,group,offset,limit);
  });
});
