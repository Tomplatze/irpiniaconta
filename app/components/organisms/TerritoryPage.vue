<script setup lang="ts">
import type { SectionMap, TerritoryMetric, TerritoryResponse } from '../../../shared/sections';
import MunicipalMetricMap from '../molecules/MunicipalMetricMap.vue';
import MetricStory from '../molecules/MetricStory.vue';
import CropHighlight from '../molecules/CropHighlight.vue';
import CropRadarSection from './CropRadarSection.vue';
import AgriculturalRadarSection from './AgriculturalRadarSection.vue';
import EconomicRadarSection from './EconomicRadarSection.vue';
import MunicipalRecords from '../molecules/MunicipalRecords.vue';
import TopicNavigator from './TopicNavigator.vue';
import TopicIllustration from '../atoms/TopicIllustration.vue';
import MunicipalCrest from '../atoms/MunicipalCrest.vue';
import type { MunicipalCrestManifest } from '../../../shared/municipalCrests';
import { formatHeadlineValue, unitLabel } from '../../utils/presentation';
import { sectionPeriod } from '../../utils/sections';
import { metricVisual, visibleStoryMetrics } from '../../utils/metricVisuals';
import { chapterDescriptions } from '../../utils/editorialCopy';
const props = defineProps<{ code?: string; comparison?: boolean; category?: string }>();
const route = useRoute();
const router = useRouter();
const initialCodes = typeof route.query.codes==='string' ? route.query.codes.split(',') : ['064033','064036'];
const codes = ref(initialCodes);
const categoryFilter = ref('all');
const mapMetricId = ref('irpef_income_mean');
const query = computed(() => props.comparison ? {codes:codes.value.join(',')} : props.code ? {code:props.code} : {});
const [territoryResult, mapResult, crestResult] = await Promise.all([
  useFetch<TerritoryResponse>('/api/territory',{query,key:`territory-${props.category ?? 'all'}-${props.comparison ? 'comparison' : props.code ?? 'province'}`}),
  useFetch<SectionMap>('/api/section-map'),
  useFetch<MunicipalCrestManifest>('/api/municipal-crests', {key: 'municipal-crests'}),
]);
const { data, status, error } = territoryResult;
const { data: map } = mapResult;
const { data: crests } = crestResult;
if (error.value?.statusCode===404 || error.value?.statusCode===400) throw createError({statusCode:error.value.statusCode,statusMessage:'Territorio non valido'});
const municipalCrest = computed(() => crests.value?.records.find(crest => crest.code === props.code));
const consistent = computed(() => data.value && (props.comparison ? data.value.scopes.map(item=>item.code).join(',')===codes.value.join(',') : data.value.scopes[0]?.code===(props.code ?? null)));
const allMetrics = computed(() => data.value?.categories.flatMap(category=>category.metrics) ?? []);
const topic = computed(() => data.value?.categories.find(item=>item.id===props.category));
if(props.category && data.value && !topic.value) throw createError({statusCode:404,statusMessage:'Sezione non trovata'});
if(topic.value) mapMetricId.value=topic.value.primary;
const mapCategories = computed(() => props.category ? data.value?.categories.filter(item=>item.id===props.category) ?? [] : data.value?.categories ?? []);
const mapMetrics = computed(() => mapCategories.value.flatMap(category=>category.metrics));
const mapMetric = computed(() => mapMetrics.value.find(metric=>metric.id===mapMetricId.value) ?? mapMetrics.value[0]);
const scopeName = computed(() => props.comparison ? 'I comuni, a confronto.' : data.value?.scopes[0]?.name ?? 'Irpinia');
const visibleCategories = computed(() => data.value?.categories.filter(item=>props.category ? item.id===props.category : categoryFilter.value==='all' || item.id===categoryFilter.value) ?? []);
const headlines = computed(() => (props.code ? ['population','irpef_income_mean','soil_consumed_pct'] : ['population','irpef_income_mean','asia_local_units']).map(id=>allMetrics.value.find(metric=>metric.id===id)).filter(item=>item!==undefined));
/** Pair only consecutive compact stories; longer or unpaired stories occupy the full row. */
function storyRows(metrics: TerritoryMetric[]): TerritoryMetric[][] {
  const result: TerritoryMetric[][] = [];
  for (const metric of visibleStoryMetrics(metrics)) {
    const previous = result.at(-1);
    const compact = metricVisual(metric) === 'counter' && !metric.has_monthly;
    if (compact && previous?.length === 1 && metricVisual(previous[0]!) === 'counter' && !previous[0]!.has_monthly) previous.push(metric);
    else result.push([metric]);
  }
  return result;
}
const topicDestinations = computed(() => props.category ? Object.fromEntries((data.value?.categories ?? []).map(category=>[category.id,`/sezioni/${category.id}${props.code ? '?code='+props.code : ''}#tema-${category.id}`])) : undefined);
useHead({title:computed(()=>`${topic.value ? topic.value.label+' · '+scopeName.value : props.comparison ? 'Confronta i comuni' : scopeName.value} — IrpiniaConta`)});
watch(()=>route.query.codes, value => {
  if(props.comparison && typeof value==='string' && value!==codes.value.join(',')) codes.value=value.split(',');
});
/** Synchronize URL changes directly from user actions, avoiding competing navigation watchers. */
function updateCodes(next: string[]): void {
  codes.value=next;
  void router.replace({path:'/confronta',query:{codes:next.join(',')}});
}
/** Preserve selection order while changing one comparison slot. */
function changeComparisonTown(index: number, event: Event): void {
  const value=(event.target as HTMLSelectElement).value;
  updateCodes(codes.value.map((code,position)=>position===index ? value : code));
}
/** Keep the selected scope in the canonical, shareable municipal route. */
function selectTown(event: Event): void {
  const target = event.target as HTMLSelectElement;
  void navigateTo(props.category ? {path:`/sezioni/${props.category}`,query:target.value ? {code:target.value} : {}} : target.value ? `/comuni/${target.value}` : '/');
}
/** Add the first unselected registry entry without duplicating a comparison slot. */
function addTown(): void {
  const town = data.value?.municipalities.find(item=>!codes.value.includes(item.code));
  if(town && codes.value.length<4) updateCodes([...codes.value,town.code]);
}
</script>
<template>
  <div class="territory-page" :class="{'territory-page--municipality':code && !category,'territory-page--topic':category}" :data-municipality="code">
    <nav v-if="code || category" class="page-breadcrumb" aria-label="Percorso"><NuxtLink to="/">L’Irpinia</NuxtLink><span aria-hidden="true">/</span><NuxtLink v-if="code" to="/comuni">I comuni</NuxtLink><span v-if="code" aria-hidden="true">/</span><span aria-current="page">{{ topic ? topic.label+(code ? ' · '+scopeName : '') : scopeName }}</span></nav>
    <header class="territory-hero">
      <div class="territory-introduction">
        <p class="eyebrow">{{ topic ? topic.intro : comparison ? 'Stessa scala, storie diverse' : code ? 'Il ritratto di un comune' : 'L’Irpinia, attraverso i dati' }}</p>
        <div class="municipality-heading"><MunicipalCrest v-if="code && !category" :crest="municipalCrest" :name="scopeName" large /><h1><template v-if="topic">{{ topic.label }}<span class="hero-title-sub">{{ code ? scopeName : 'In Irpinia.' }}</span></template><template v-else-if="comparison">I comuni,<br><em>a confronto.</em></template><template v-else-if="code">{{ scopeName }}<span class="municipality-title-caption">Il territorio, i suoi numeri.</span></template><template v-else>Ogni numero<br>racconta <em>l’Irpinia.</em></template></h1></div>
        <p v-if="code && !category" class="municipality-identity"><span class="municipality-marker" aria-hidden="true">●</span> Provincia di Avellino <span>ISTAT {{ code }}</span></p>
        <p class="territory-lead">{{ topic ? 'Tutti gli indicatori del tema, con grafici, periodi e fonti: '+(code ? 'il dettaglio di '+scopeName+'.' : 'il quadro dell’intera Irpinia.') : comparison ? 'Sovrapponi le storie di due, tre o quattro comuni. Gli stessi indicatori, gli stessi periodi e una scala condivisa.' : code ? 'La pagina di '+scopeName+': residenti, attività, servizi e paesaggio. Ogni indicatore riguarda questo comune; gli anni e le fonti accompagnano i numeri.' : 'Persone, paesaggi, risorse e cambiamenti. Un ritratto del territorio da leggere con gli occhi, un dato alla volta.' }}</p>
        <label v-if="category && data" class="territory-scope-picker">Territorio del tema<select :value="code ?? ''" @change="selectTown"><option value="">Tutta l’Irpinia</option><option v-for="town in data.municipalities" :key="town.code" :value="town.code">{{ town.name }}</option></select></label>
        <div class="hero-actions"><a class="action-primary" href="#temi">{{ comparison ? 'Guarda i grafici' : 'Esplora i dati' }} ↓</a><NuxtLink v-if="!comparison" :to="{path:'/confronta',query:code ? {codes:`${code},${code==='064033' ? '064036' : '064033'}`} : {}}">Confronta i comuni ↗</NuxtLink><NuxtLink v-else to="/">Tutta l’Irpinia ↗</NuxtLink></div>
        <NuxtLink v-if="code && !category" class="municipality-switch" to="/comuni">Esplora un altro comune ↗</NuxtLink>
        <p class="hero-footnote">{{ topic ? 'Un tema' : '10 temi' }} · {{ topic ? mapMetrics.length : allMetrics.length }} indicatori selezionati · {{ code ? scopeName : '118 comuni' }}<br>Ogni dato conserva il suo anno e la sua fonte.</p>
      </div>
      <section v-if="mapMetric && map" id="mappa-territorio" class="territory-map" aria-label="Esplora i comuni sulla mappa">
        <label class="map-indicator-picker">Colora la mappa per<select v-model="mapMetricId"><optgroup v-for="category in mapCategories" :key="category.id" :label="category.label"><option v-for="metric in category.metrics" :key="metric.id" :value="metric.id">{{ metric.label }}</option></optgroup></select></label>
        <MunicipalMetricMap :map="map" :values="mapMetric.distribution" :unit="mapMetric.unit" :selected-code="code ?? ''" :period="sectionPeriod(mapMetric.latest_period,mapMetric.id)" navigation />
        <p class="map-period-label">{{ mapMetric.label }} · {{ sectionPeriod(mapMetric.latest_period,mapMetric.id) }}</p>
      </section>
    </header>
    <div v-if="!comparison && !category && consistent" class="territory-highlights" :aria-label="code ? 'Tre dati di '+scopeName : 'Tre dati dell’Irpinia'">
      <a v-for="metric in headlines" :key="metric.id" :href="`#${metric.id}`"><span>{{ metric.label }}</span><strong>{{ formatHeadlineValue(metric.series[0]!.current.value,metric.unit) }} <small>{{ unitLabel(metric.unit) }}</small></strong><span>{{ sectionPeriod(metric.latest_period,metric.id) }}</span></a>
    </div>
    <section v-if="comparison && data" class="comparison-pickers" aria-label="Comuni da confrontare">
      <div v-for="(selected,index) in codes" :key="index" class="comparison-picker" :class="`series-tone-${index}`"><label :for="`town-${index}`"><i :class="`series-symbol-${index}`" />Comune {{ index+1 }}</label><select :id="`town-${index}`" :value="selected" @change="changeComparisonTown(index,$event)"><option v-for="town in data.municipalities" :key="town.code" :value="town.code" :disabled="town.code!==selected && codes.includes(town.code)">{{ town.name }}</option></select><button v-if="codes.length>2" @click="updateCodes(codes.filter((_,position)=>position!==index))">Rimuovi</button></div>
      <button v-if="codes.length<4" class="add-comparison" @click="addTown">＋ Aggiungi un comune</button>
    </section>
    <p v-if="error" class="notice" role="alert">Non riusciamo a mostrare i dati in questo momento. Riprova più tardi.</p>
    <p v-if="status==='pending'" class="notice" role="status">Aggiornamento dei grafici per i territori scelti…</p>
    <div id="temi" class="theme-toolbar"><div><span class="eyebrow">{{ topic ? 'Un capitolo dell’atlante' : 'Il territorio in dieci capitoli' }}</span><h2>{{ topic ? 'Il tema prende forma.' : comparison ? 'Le differenze prendono forma.' : code ? 'Dentro '+scopeName+'.' : 'Una storia fatta di dati.' }}</h2></div><label v-if="comparison">Mostra<select v-model="categoryFilter"><option value="all">Tutti i temi</option><option v-for="category in data?.categories" :key="category.id" :value="category.id">{{ category.label }}</option></select></label></div>
    <TopicNavigator v-if="consistent" :categories="category ? data?.categories ?? [] : visibleCategories" :order="data?.categories.map(category => category.id) ?? []" :destinations="topicDestinations" :current-id="category" :municipality-name="code ? scopeName : undefined" />
    <div v-if="consistent" class="territory-chapters" :aria-busy="status==='pending'">
      <section v-for="category in visibleCategories" :id="`tema-${category.id}`" :key="category.id" class="territory-chapter" :aria-labelledby="`heading-${category.id}`">
        <header class="chapter-heading"><TopicIllustration :topic="category.id" class="chapter-illustration" /><div><p class="eyebrow">{{ category.intro }}</p><h2 :id="`heading-${category.id}`">{{ category.label }}</h2></div></header>
        <p v-if="chapterDescriptions[category.id]" class="chapter-description">{{ chapterDescriptions[category.id] }}</p>
        <div class="story-grid">
          <div v-for="row in storyRows(category.metrics)" :key="row[0]!.id" class="story-row" :class="{'story-row--pair':row.length===2}"><MetricStory v-for="metric in row" :key="metric.id" :metric="metric" /></div>
          <CropHighlight v-if="category.id==='agriculture' && category.metrics.find(metric => metric.id==='utilised_agricultural_area')" :metric="category.metrics.find(metric => metric.id==='utilised_agricultural_area')!" />
        </div>
        <div v-if="code && category.id==='administration'" class="municipal-extra-records"><MunicipalRecords :code="code" group="authority" label="Enti e amministrazioni nel comune" /></div>
        <div v-if="code && category.id==='culture'" class="municipal-extra-records"><MunicipalRecords :code="code" group="heritage" label="Altri luoghi nel catalogo provinciale" /></div>
        <div v-if="code && category.id==='services'" class="municipal-extra-records"><MunicipalRecords :code="code" group="province_schools" label="Scuole nel catalogo provinciale" /></div>
        <div v-if="code && category.id==='mobility'" class="municipal-extra-records"><MunicipalRecords :code="code" group="works" label="Ordinanze e cantieri nel catalogo provinciale" /></div>
        <EconomicRadarSection v-if="category.id==='economy' && category.metrics.find(metric => metric.id==='asia_local_units')" :metric="category.metrics.find(metric => metric.id==='asia_local_units')!" />
        <CropRadarSection v-if="category.id==='agriculture' && category.metrics.find(metric => metric.id==='utilised_agricultural_area')" :metric="category.metrics.find(metric => metric.id==='utilised_agricultural_area')!" />
        <AgriculturalRadarSection v-if="category.id==='agriculture' && category.metrics.find(metric => metric.id==='livestock_farms')" :metric="category.metrics.find(metric => metric.id==='livestock_farms')!" kind="livestock" />
        <AgriculturalRadarSection v-if="category.id==='agriculture' && category.metrics.find(metric => metric.id==='organic_area')" :metric="category.metrics.find(metric => metric.id==='organic_area')!" kind="organic" />
      </section>
    </div>
  </div>
</template>
