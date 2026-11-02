<script setup lang="ts">
import type { TerritoryMetric } from '../../../shared/sections';
import OverlayChart from './OverlayChart.vue';
import MonthlyHeatmap from './MonthlyHeatmap.vue';
import LatestDistribution from './LatestDistribution.vue';
import DemographicFlowChart from './DemographicFlowChart.vue';
import PercentageVisual from './PercentageVisual.vue';
import TopicIllustration from '../atoms/TopicIllustration.vue';
import MunicipalRecords from './MunicipalRecords.vue';
import { metricVisual, sourcePublishers, historyVariant, historyPresentation, metricTitle, storySources } from '../../utils/metricVisuals';
import { formatHeadlineValue, formatValue, unitLabel, statusLabel, formatDate } from '../../utils/presentation';
import { sectionPeriod } from '../../utils/sections';
import { licenseDescription } from '../../utils/sourcePresentation';
import { historicalDescription, historyScope, metricDescription, summaryDescription } from '../../utils/editorialCopy';
const props = defineProps<{metric:TerritoryMetric}>();
const visual = computed(() => props.metric.id==='state_school_sites' && props.metric.series.length===1 && props.metric.series[0]?.code ? 'counter' : metricVisual(props.metric));
const title = computed(() => metricTitle(props.metric));
const description = computed(() => metricDescription(props.metric.id,props.metric.description));
const historical = computed(() => historyPresentation(props.metric));
const sources = computed(() => storySources(props.metric));
const provincial = computed(() => props.metric.series.length===1 && props.metric.series[0]?.code===null);
const municipal = computed(() => props.metric.series.length===1 && props.metric.series[0]?.code!==null);
const municipalCode = computed(() => municipal.value ? props.metric.series[0]?.code : null);
const recordGroups: Record<string,{group:string;label:string}> = {
  state_school_sites:{group:'schools',label:'Elenco delle sedi scolastiche'}, pharmacy_location_count:{group:'pharmacies',label:'Elenco delle farmacie'},
  pnrr_projects:{group:'pnrr',label:'Elenco dei progetti PNRR'}, cohesion_projects:{group:'cohesion',label:'Elenco dei progetti di coesione'},
  digital_allocated_eur:{group:'digital',label:'Elenco delle candidature per il digitale'}, fortified_sites:{group:'fortified',label:'Elenco delle fortificazioni'},
  historic_centres:{group:'historic',label:'Elenco dei centri storici mappati'}, cultural_places:{group:'cultural',label:'Elenco dei luoghi della cultura'},
  province_libraries_listed_records:{group:'libraries',label:'Elenco delle biblioteche'}
};
const recordGroup = computed(() => recordGroups[props.metric.id]);
const catalogueCounter = computed(() => props.metric.category==='culture' || props.metric.id==='pharmacy_location_count');
const chartSeries = computed(() => historical.value?.series.map(item => ({code:item.code ?? 'province',name:item.name,values:item.history.values})) ?? []);
const monthly = computed(() => props.metric.series.filter(item => item.monthly).map(item => ({code:item.code ?? 'province',name:item.name,values:item.monthly!.values})));
const publishers = computed(() => sourcePublishers(props.metric));
const flow = computed(() => visual.value==='flows' ? props.metric.demographic_flow : undefined);
const flowCurrent = computed(() => flow.value?.series[0]?.values.find(point => point.period===props.metric.latest_period));
const provisional = computed(() => /provisional|provvisor/i.test(flow.value?.period_notes[props.metric.latest_period] ?? ''));
const singlePeriod = computed(() => {
  const periods = props.metric.series[0]?.history.values.filter(point => point.status==='observed' && point.value!==null).map(point=>point.period) ?? [];
  return periods.length===1 ? sectionPeriod(periods[0]!,props.metric.id) : null;
});
const historyRange = computed(() => historical.value ? `${historical.value.metric.periods[0]}–${historical.value.metric.periods.at(-1)}` : '');
const change = computed(() => {
  if (props.metric.series.length!==1 || !historical.value) return null;
  const points = historical.value.series[0]!.history.values.filter(point => point.status==='observed' && point.value!==null);
  const first = points[0]; const last = points.at(-1);
  if (!first || !last || first.period===last.period || first.value!<=0) return null;
  const difference = historical.value.metric.unit==='%' ? last.value!-first.value! : (last.value!-first.value!)/first.value!*100;
  return {first:first.period,last:last.period,value:difference,unit:historical.value.metric.unit==='%' ? 'punti percentuali' : '%'};
});
/** Shorten funding headlines while retaining exact original quantities in source evidence. */
function headline(value:number|null):string {
  if (value!==null && props.metric.unit==='EUR' && Math.abs(value)>=1_000_000) return formatValue(value/(Math.abs(value)>=1_000_000_000 ? 1_000_000_000 : 1_000_000));
  return formatHeadlineValue(value,props.metric.unit);
}
/** Keep magnitude words beside the unit instead of breaking the main numeral. */
function headlineUnit(value:number|null):string {
  if (value!==null && props.metric.unit==='EUR' && Math.abs(value)>=1_000_000) return Math.abs(value)>=1_000_000_000 ? 'miliardi di €' : 'milioni di €';
  return unitLabel(props.metric.unit);
}
</script>
<template>
  <article :id="metric.id" class="metric-story" :class="[`metric-story--${visual}`,{'metric-story--catalogue':catalogueCounter}]">
    <header class="story-heading"><div class="story-title"><div class="story-intro"><h3>{{ title }}</h3><p class="story-period">{{ sectionPeriod(metric.latest_period,metric.id) }}<span v-if="provisional"> · dati provvisori</span></p></div><TopicIllustration v-if="visual!=='counter'" :topic="metric.category" :metric="metric.id" /></div></header>
    <div v-if="flow && flowCurrent" class="flow-headlines">
      <div class="flow-count flow-count--positive"><span>{{ flow.positive.label }}</span><strong>{{ flowCurrent.positive.status==='observed' ? formatValue(flowCurrent.positive.value,'persons') : '—' }}</strong><small>persone nell’anno</small></div>
      <div class="flow-count flow-count--negative"><span>{{ flow.negative.label }}</span><strong>{{ flowCurrent.negative.status==='observed' ? formatValue(flowCurrent.negative.value,'persons') : '—' }}</strong><small>persone nell’anno</small></div>
    </div>
    <div v-else class="story-statistic">
      <div class="story-values" :class="{'story-values--multiple':metric.series.length>1}"><div v-for="(item,index) in metric.series" :key="item.code ?? 'province'" :class="`series-tone-${index}`"><span v-if="metric.series.length>1" class="story-scope"><i :class="`series-symbol-${index}`" />{{ item.name }}</span><p class="story-number">{{ item.current.status==='observed' ? headline(item.current.value) : '—' }} <small>{{ headlineUnit(item.current.value) }}</small></p><p v-if="!catalogueCounter" class="story-method">{{ item.current.status==='observed' ? summaryDescription(item.current.summary_label) : statusLabel(item.current.status) }}<template v-if="!item.code && item.current.status==='observed'"> · {{ item.current.coverage }}/118 comuni</template></p><p v-else-if="item.current.status!=='observed'" class="story-method">{{ statusLabel(item.current.status) }}</p></div></div>
      <TopicIllustration v-if="visual==='counter'" :topic="metric.category" :metric="metric.id" class="stat-illustration" />
    </div>
    <p class="story-description">{{ description }}</p><p v-if="catalogueCounter" class="counter-source">{{ publishers }}</p>
    <p v-if="flow && flowCurrent" class="flow-balance">{{ flow.kind==='natural' ? 'Differenza tra nati e morti' : 'Differenza tra arrivi e partenze' }}: <strong>{{ flowCurrent.balance.status==='observed' ? (flowCurrent.balance.value!>0 ? '+' : '')+formatValue(flowCurrent.balance.value,'persons')+' persone' : 'non disponibile' }}</strong></p>
    <DemographicFlowChart v-if="flow" :flow="flow" :latest-period="metric.latest_period" />
    <template v-else-if="visual==='history' && historical">
      <div v-if="historical.separate" :id="historical.metric.id" class="history-context"><h4>{{ historical.metric.label }} · {{ historyRange }}</h4><p v-if="metric.id==='population'">Il grafico mostra i residenti al 31 dicembre degli anni disponibili. La stima al 1° gennaio {{ metric.latest_period.slice(0,4) }} è un dato distinto.</p><p v-else>Il grafico mostra i censimenti precedenti, separati dal dato {{ metric.latest_period }} qui sopra: nel tempo le definizioni possono essere cambiate.</p></div>
      <p v-for="item in historical.series.filter(series => !series.code)" :key="item.name" class="visual-note">Per confrontare gli anni, il grafico considera {{ historyScope(item.history.scope) }}. <strong v-if="item.history.values.at(-1)?.coverage!==metric.series[0]?.current.coverage">Il dato più recente qui sopra riguarda invece {{ metric.series[0]?.current.coverage }} comuni: i territori considerati sono diversi.</strong></p>
      <OverlayChart :series="chartSeries" :unit="historical.metric.unit" :label="historical.metric.label" :metric-id="historical.metric.id" :variant="historyVariant(metric)" />
      <p v-if="change" class="story-change"><strong>{{ change.value>0 ? '+' : '' }}{{ formatValue(change.value) }}{{ change.unit==='%' ? '%' : ' '+change.unit }}</strong> dal {{ change.first }} al {{ change.last }} · per i dati mostrati nel grafico</p>
    </template>
    <PercentageVisual v-else-if="visual==='percentage'" :value="metric.series[0]!.current.value" :status="metric.series[0]!.current.status" :soil="metric.id==='soil_consumed_pct'" :median="provincial && metric.aggregation==='median'" />
    <LatestDistribution v-else-if="visual==='distribution'" :metric="metric" />
    <p v-else-if="municipal && !catalogueCounter && metric.category!=='investments' && metric.id!=='state_school_sites'" class="snapshot-note">{{ metric.id==='foreign_residents' ? 'Questa scheda mostra la stima al 1° gennaio 2026. I dati del 2024 sono disponibili nella raccolta delle fonti.' : singlePeriod ? 'Per questo comune abbiamo un solo dato: '+singlePeriod+'.' : 'Per questo comune non abbiamo dati di altri anni da confrontare.' }}</p>
    <template v-if="monthly.length"><p class="monthly-heading">Mese per mese · {{ metric.latest_period }}</p><MonthlyHeatmap v-if="monthly.length===1" :series="monthly" :unit="metric.unit" :label="`${metric.label}, medie mensili`" :metric-id="metric.id" /><OverlayChart v-else :series="monthly" :unit="metric.unit" :label="`${metric.label}, medie mensili`" :metric-id="metric.id" /><p class="visual-note">{{ metric.series[0]?.monthly?.scope }}</p></template>
    <MunicipalRecords v-if="municipalCode && recordGroup" :code="municipalCode" :group="recordGroup.group" :label="recordGroup.label" />
    <details class="story-source"><summary>Significato e fonti del dato</summary><p>{{ description }}</p><p>Periodo dell’ultimo dato: {{ sectionPeriod(metric.latest_period,metric.id) }}.</p><template v-if="historical?.separate"><p><strong>{{ historical.metric.label }} · {{ historyRange }}</strong></p><p>{{ historicalDescription(historical.metric.description) }}</p></template><p v-if="metric.historical && !historical">{{ historicalDescription(metric.historical.metric.description) }} Per il comune selezionato non abbiamo abbastanza dati di anni diversi per mostrare un andamento.</p><section v-for="source in sources" :key="`${source.id}:${source.url}`" class="source-citation"><strong>{{ source.publisher }}</strong><a :href="source.url" target="_blank" rel="noreferrer">{{ source.title }} ↗</a><span>Accesso alla fonte verificato il {{ formatDate(source.verified_at) }}</span><span v-if="source.license">Licenza dichiarata: {{ licenseDescription(source.license) }}</span></section><p v-if="provincial">L’ultimo dato comprende {{ metric.series[0]!.current.coverage }} comuni su 118. Se un dato manca, non significa che sia zero.</p></details>
  </article>
</template>
