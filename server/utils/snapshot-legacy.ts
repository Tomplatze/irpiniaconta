import type { Comparison, Dataset, Indicator, Overview, ValueStatus } from '../../shared/types';
import type { Catalogue, EntityPage, Exploration, Series } from '../../shared/catalogue';
import { entityRecord } from './scope';
import { snapshotObject, snapshotSource } from './snapshot';

type Observation = { municipality_code: string; indicator_id: string; period: string; value: number | string | null; status: ValueStatus };
async function state(): Promise<{overview:Overview;observations:Observation[]}> {
  const [overview,source]=await Promise.all([snapshotObject<Overview>('overview.gz'),snapshotSource()]);
  return {overview,observations:source.observations as Observation[]};
}
function indicatorFor(overview:Overview,id:string):{indicator:Indicator;dataset:Dataset}{
  for(const dataset of overview.datasets){const indicator=dataset.indicators.find(item=>item.id===id);if(indicator)return {indicator,dataset};}
  throw createError({statusCode:404,statusMessage:'Unknown indicator'});
}
/** Explore the requested published period without querying PostgreSQL. */
export async function snapshotExplore(id:string,selectedPeriod?:string):Promise<Exploration>{
  const {overview,observations}=await state();const {indicator}=indicatorFor(overview,id);const period=selectedPeriod??indicator.latest_period;
  if(!period||!indicator.periods.includes(period))throw createError({statusCode:404,statusMessage:'Unavailable period'});
  const cells=new Map(observations.filter(row=>row.indicator_id===id&&row.period===period).map(row=>[row.municipality_code,row]));
  return {indicator,period,values:overview.municipalities.map(town=>{const cell=cells.get(town.code);return {...town,value:cell?.value==null?null:Number(cell.value),status:cell?.status??'unavailable'};})};
}
/** Reconstruct published observations for the requested municipal series. */
export async function snapshotSeries(id:string,codes:string[]):Promise<Series>{
  const {overview,observations}=await state();const {indicator,dataset}=indicatorFor(overview,id);
  const municipalities=codes.map(code=>{const town=overview.municipalities.find(item=>item.code===code);if(!town)throw createError({statusCode:404,statusMessage:'Unknown municipality'});return town;});
  const cells=new Map(observations.filter(row=>row.indicator_id===id&&codes.includes(row.municipality_code)).map(row=>[`${row.municipality_code}:${row.period}`,row]));
  return {indicator,dataset,municipalities:municipalities.map(town=>({...town,values:[...indicator.periods].sort().map(period=>{const cell=cells.get(`${town.code}:${period}`);return {period,value:cell?.value==null?null:Number(cell.value),status:cell?.status??'unavailable'};})}))};
}
/** Reconstruct the comparison using exact source periods and missing-data states. */
export async function snapshotComparison(codes:string[],id?:string,selectedPeriod?:string):Promise<Comparison>{
  const {overview,observations}=await state();
  const municipalities=codes.map(code=>{const town=overview.municipalities.find(item=>item.code===code);if(!town)throw createError({statusCode:404,statusMessage:'Municipality not in the current ISTAT registry'});return town;});
  const indicators=overview.datasets.flatMap(dataset=>dataset.indicators);if(id&&!indicators.some(item=>item.id===id))throw createError({statusCode:404,statusMessage:'Unknown indicator'});
  const cells=new Map(observations.filter(row=>codes.includes(row.municipality_code)).map(row=>[`${row.municipality_code}:${row.indicator_id}:${row.period}`,row]));
  const rows=indicators.filter(item=>!id||item.id===id).map(indicator=>{const period=selectedPeriod??indicator.latest_period;if(selectedPeriod&&!indicator.periods.includes(selectedPeriod))throw createError({statusCode:404,statusMessage:'Period unavailable for this indicator'});return {indicator,dataset_id:indicator.dataset_id,period,measurements:municipalities.map(town=>{const row=cells.get(`${town.code}:${indicator.id}:${period}`);return {code:town.code,name:town.name,value:row?.value==null?null:Number(row.value),status:row?.status??'unavailable' as ValueStatus};})};});
  return {municipalities,rows};
}
/** Apply the existing exact filters and pagination to the private entity projection. */
export async function snapshotEntities(offset:number,limit:number,code?:string,category?:string):Promise<EntityPage>{
  const [scope,source,overview]=await Promise.all([snapshotObject<Catalogue>('catalogue.gz'),snapshotSource(),snapshotObject<Overview>('overview.gz')]);
  if(category&&!scope.categories.some(item=>item.id===category))throw createError({statusCode:404,statusMessage:'Unknown category'});
  if(code&&!overview.municipalities.some(item=>item.code===code))throw createError({statusCode:404,statusMessage:'Unknown municipality'});
  const ids=new Set(scope.sources.filter(item=>!category||item.category_id===category).map(item=>item.dataset?.id).filter((id):id is string=>typeof id==='string'));
  const rows=source.entities.filter(row=>ids.has(String(row.dataset_id))&&(!code||row.municipality_code===code));
  return {total:rows.length,records:rows.slice(offset,offset+limit).map(entityRecord),limit,offset};
}
