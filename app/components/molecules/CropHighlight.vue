<script setup lang="ts">
import type { TerritoryMetric } from '../../../shared/sections';
import { formatValue, statusLabel, unitLabel } from '../../utils/presentation';
import { historicalDescription, historyScope, summaryDescription } from '../../utils/editorialCopy';
import OverlayChart from './OverlayChart.vue';
import TopicIllustration from '../atoms/TopicIllustration.vue';
const props = defineProps<{ metric: TerritoryMetric }>();
const fruit = computed(() => props.metric.breakdown?.find(entry => entry.metric.id === 'breakdown_crops_fruit'));
const historical = computed(() => fruit.value?.historical);
const chartSeries = computed(() => historical.value?.series.map(item => ({code:item.code ?? 'province',name:item.name,values:item.history.values})) ?? []);
const hasHistory = computed(() => chartSeries.value.some(item => item.values.filter(point => point.status==='observed' && point.value!==null).length > 1));
const change = computed(() => {
  if (chartSeries.value.length !== 1) return null;
  const points = chartSeries.value[0]!.values.filter(point => point.status==='observed' && point.value!==null);
  const first = points[0]; const last = points.at(-1);
  if (!first || !last || first.period===last.period || first.value!<=0) return null;
  return {first:first.period,last:last.period,value:(last.value!-first.value!)/first.value!*100};
});
</script>
<template>
  <article v-if="fruit" id="fruit-area" class="metric-story crop-highlight">
    <header class="story-heading"><div class="story-title"><div class="story-intro"><h3>Fruttiferi e frutta a guscio</h3><p class="story-period">{{ fruit.metric.latest_period }}</p></div><TopicIllustration topic="agriculture" metric="fruit_area" /></div></header>
    <div class="story-values" :class="{'story-values--multiple':fruit.series.length>1}">
      <div v-for="(item, index) in fruit.series" :key="item.code ?? 'province'" :class="`series-tone-${index}`">
        <span v-if="fruit.series.length>1" class="story-scope">{{ item.name }}</span>
        <p class="story-number">{{ item.current.status==='observed' ? formatValue(item.current.value, fruit.metric.unit) : '—' }} <small>{{ unitLabel(fruit.metric.unit) }}</small></p>
        <p class="story-method">{{ item.current.status==='observed' ? summaryDescription(item.current.summary_label) : statusLabel(item.current.status) }}<template v-if="item.code===null && item.current.status==='observed'"> · {{ item.current.coverage }}/118 comuni</template></p>
      </div>
    </div>
    <p class="story-description">Superfici delle aziende agricole con sede nel territorio, dal censimento ISTAT. La categoria comprende fruttiferi, frutta a guscio e piccoli frutti; non distingue castagneti e noccioleti.</p>
    <template v-if="historical && hasHistory">
      <div class="history-context"><h4>{{ historical.metric.label }} · {{ historical.metric.periods[0] }}–{{ historical.metric.periods.at(-1) }}</h4><p>Il grafico mostra i censimenti precedenti separatamente dal dato {{ fruit.metric.latest_period }}. Le definizioni possono essere cambiate nel tempo.</p></div>
      <p v-for="item in historical.series.filter(series => !series.code)" :key="item.name" class="visual-note">Per confrontare gli anni, il grafico considera {{ historyScope(item.history.scope) }}. <strong v-if="item.history.values.at(-1)?.coverage!==fruit.series[0]?.current.coverage">Il dato più recente sopra riguarda {{ fruit.series[0]?.current.coverage }} comuni: non sono gli stessi considerati nel grafico.</strong></p>
      <OverlayChart :series="chartSeries" :unit="historical.metric.unit" :label="historical.metric.label" :metric-id="historical.metric.id" />
      <p v-if="change" class="story-change"><strong>{{ change.value>0 ? '+' : '' }}{{ formatValue(change.value) }}%</strong> dal {{ change.first }} al {{ change.last }} · nei dati mostrati</p>
    </template>
    <p v-else-if="historical" class="snapshot-note">Per questo territorio non abbiamo abbastanza dati degli anni precedenti per mostrare come è cambiato il valore.</p>
    <details class="story-source"><summary>Significato e fonti del dato</summary><p>I terreni sono attribuiti alla sede aziendale e possono trovarsi in altri comuni. Il dato riguarda l’insieme della categoria, non singoli prodotti o produzioni certificate.</p><p v-if="historical">{{ historicalDescription(historical.metric.description) }}</p><section v-for="source in [...fruit.metric.sources, ...(historical?.metric.sources ?? [])]" :key="source.id" class="source-citation"><strong>{{ source.publisher }}</strong><a :href="source.url" target="_blank" rel="noreferrer">{{ source.title }} ↗</a></section></details>
  </article>
</template>
