<script setup lang="ts">
type Point = { year: number; value: number };
type Series = { name: string; points: Point[] };
const props = defineProps<{ title: string; description: string; unit: string; series: Series[]; note: string }>();
const allPoints = computed(() => props.series.flatMap(series => series.points));
const firstYear = computed(() => Math.min(...allPoints.value.map(point => point.year)));
const lastYear = computed(() => Math.max(...allPoints.value.map(point => point.year)));
const selectedYear = ref(lastYear.value);
const minValue = computed(() => Math.min(...allPoints.value.map(point => point.value)));
const maxValue = computed(() => Math.max(...allPoints.value.map(point => point.value)));
const step = computed(() => {
  const range = maxValue.value - minValue.value;
  return range > 20 ? 5 : range > 8 ? 2 : range > 4 ? 1 : 0.5;
});
const lower = computed(() => Math.max(0, Math.floor((minValue.value - step.value * 0.4) / step.value) * step.value));
const upper = computed(() => Math.ceil((maxValue.value + step.value * 0.4) / step.value) * step.value);
const axisTicks = computed(() => Array.from({ length: Math.round((upper.value - lower.value) / step.value) + 1 }, (_, i) => lower.value + i * step.value));
const yearTicks = computed(() => [...new Set([firstYear.value, ...Array.from({ length: lastYear.value - firstYear.value + 1 }, (_, i) => firstYear.value + i).filter(year => year % 5 === 0), lastYear.value])]);
const x = (year: number) => ((year - firstYear.value) / Math.max(1, lastYear.value - firstYear.value)) * 100;
const y = (value: number) => 100 - (value - lower.value) / (upper.value - lower.value) * 100;
const path = (points: Point[]) => points.map((point, index) => `${index ? 'L' : 'M'} ${x(point.year).toFixed(2)} ${y(point.value).toFixed(2)}`).join(' ');
const valueAt = (item: Series, year: number) => item.points.find(point => point.year === year)?.value;
const format = (value: number) => value.toLocaleString('it-IT', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
/** Select the nearest observed year from the pointer's position in the plotting area. */
function selectFromPointer(event: PointerEvent): void {
  const target = event.currentTarget;
  if (!(target instanceof SVGElement)) return;
  const bounds = target.getBoundingClientRect();
  const position = Math.min(1, Math.max(0, (event.clientX - bounds.left) / bounds.width));
  selectedYear.value = Math.round(firstYear.value + position * (lastYear.value - firstYear.value));
}
</script>
<template>
  <article class="trend-card">
    <header class="trend-card__intro"><div><p class="eyebrow">Serie storica · {{ firstYear }}–{{ lastYear }}</p><h3>{{ title }}</h3><p>{{ description }}</p></div><div class="trend-card__latest"><span>Provincia di Avellino · {{ lastYear }}</span><strong>{{ format(series[0]?.points.at(-1)?.value ?? 0) }}</strong><small>{{ unit }}</small></div></header>
    <div class="trend-card__readout"><div class="trend-card__readout-year"><span>Anno selezionato</span><strong>{{ selectedYear }}</strong></div><div v-for="(item, index) in series" :key="item.name" class="trend-card__readout-value"><span><i :class="`color-${index}`" />{{ item.name }}</span><strong>{{ valueAt(item, selectedYear) === undefined ? '—' : format(valueAt(item, selectedYear)!) }}</strong></div></div>
    <div class="trend-card__chart"><div class="trend-card__axis" aria-hidden="true"><span v-for="tick in [...axisTicks].reverse()" :key="tick">{{ format(tick) }}</span></div><div class="trend-card__canvas"><svg viewBox="0 0 100 100" preserveAspectRatio="none" role="img" :aria-label="`${title}, dal ${firstYear} al ${lastYear}. Seleziona un anno per confrontare i tre territori.`" @pointermove="selectFromPointer" @pointerdown="selectFromPointer"><line v-for="tick in axisTicks" :key="tick" x1="0" x2="100" :y1="y(tick)" :y2="y(tick)" class="grid-line"/><path v-for="(item,index) in series" :key="item.name" :d="path(item.points)" :class="`line-${index}`" vector-effect="non-scaling-stroke"/><line :x1="x(selectedYear)" :x2="x(selectedYear)" y1="0" y2="100" class="year-line"/></svg><div class="trend-card__markers" aria-hidden="true"><template v-for="(item,index) in series" :key="`${item.name}-point`"><span v-if="valueAt(item,selectedYear) !== undefined" class="trend-card__marker" :class="`color-${index}`" :style="{ left: `${x(selectedYear)}%`, top: `${y(valueAt(item,selectedYear)!)}%` }" /></template></div><div class="trend-card__years" aria-hidden="true"><span v-for="year in yearTicks" :key="year" :style="{ left: `${x(year)}%` }">{{ year }}</span></div></div></div>
    <label class="trend-card__control"><span>Esplora ogni anno</span><input v-model.number="selectedYear" type="range" :min="firstYear" :max="lastYear" step="1" :aria-label="`Anno per ${title}`" :aria-valuetext="`${selectedYear}`"><strong>{{ selectedYear }}</strong></label>
    <p class="trend-card__note">{{ unit }}. Scala verticale {{ format(lower) }}–{{ format(upper) }}: non parte necessariamente da zero. {{ note }}</p>
    <details class="story-source"><summary>Significato e fonti del dato</summary><p>{{ description }} {{ note }}</p><section class="source-citation"><strong>ISTAT</strong><a href="https://www.istat.it/notizia/bes-dei-territori-edizione-2025/" target="_blank" rel="noopener noreferrer">BES dei territori 2025 · tavole provinciali ↗</a><span>Pubblicato il 1° luglio 2025 · verificato il 3 novembre 2026</span><span>Elaborazione IrpiniaConta · <a href="https://creativecommons.org/licenses/by/4.0/deed.it">CC BY 4.0</a></span></section></details>
  </article>
</template>
<style scoped src="../../assets/css/health-trend.css"></style>
