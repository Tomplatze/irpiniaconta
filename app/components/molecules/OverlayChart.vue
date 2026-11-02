<script setup lang="ts">
import { buildOverlayPlot, type OverlayInput } from '../../utils/history';
import { formatValue, unitLabel } from '../../utils/presentation';
import { sectionPeriod } from '../../utils/sections';
import { useChartWidth } from '../../composables/useChartWidth';
import type { HistoryVariant } from '../../utils/metricVisuals';
const props = defineProps<{ series: OverlayInput[]; unit: string; label: string; metricId: string; variant?: HistoryVariant }>();
const figure = ref<HTMLElement | null>(null);
const width = useChartWidth(figure);
const variant = computed(() => props.series.length>1 ? 'line' : props.variant ?? 'line');
const plot = computed(() => buildOverlayPlot(props.series,width.value,{includeZero:variant.value!=='line',bars:variant.value==='bars'}));
const gradientId = `history-fill-${useId().replaceAll(':','')}`;
const active = ref('');
const reading = computed(() => {
  const period = active.value || plot.value.periods.at(-1)?.period;
  return { period, rows: props.series.map(item => ({ name: item.name, point: item.values.find(point => point.period === period) })) };
});
const readingX = computed(() => plot.value.periods.find(point=>point.period===reading.value.period)?.x);
watch(() => props.series, () => { active.value=''; });
const ticks = computed(() => {
  const periods = plot.value.periods;
  if(width.value<440 && periods.length>2) return [periods[0]!,periods.at(-1)!];
  return periods.length <= 4 ? periods : [periods[0]!,periods[Math.floor((periods.length-1)/2)]!,periods.at(-1)!];
});
const compact = (value: number): string => new Intl.NumberFormat('it-IT',{notation:'compact',maximumFractionDigits:1}).format(value);
const patterns = ['', '9 4', '2 4', '12 4 2 4'];
/** Place signed zero ticks by their value rather than assuming evenly spaced tick labels. */
const tickY = (value: number): number => 208-(value-plot.value.minimum)/(plot.value.maximum-plot.value.minimum)*180;
/** Inspect all overlaid municipalities at the same period with one keyboard stop. */
function step(direction: number): void {
  const periods = plot.value.periods;
  const index = periods.findIndex(item=>item.period===reading.value.period);
  active.value=periods[Math.max(0,Math.min(periods.length-1,index+direction))]?.period ?? '';
}
</script>
<template>
  <figure ref="figure" class="overlay-chart" :class="`overlay-chart--${variant}`">
    <svg :viewBox="`0 0 ${width} 266`" role="group" tabindex="0" :aria-label="`${label}. ${unitLabel(unit)}. ${variant==='bars' ? 'Colonne con asse da zero.' : variant==='area' ? 'Area con asse da zero.' : 'Linee su scale comuni.'} I dati mancanti restano vuoti. Usa le frecce per cambiare periodo.`" @mouseleave="active=''" @keydown.left.prevent="step(-1)" @keydown.right.prevent="step(1)">
      <defs><linearGradient v-for="(_,index) in plot.series" :id="`${gradientId}-${index}`" :key="index" :class="`series-tone-${index}`" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="currentColor" :stop-opacity="series.length > 1 ? .12 : .24" /><stop offset="100%" stop-color="currentColor" stop-opacity=".025" /></linearGradient></defs>
      <g v-for="(tick,index) in plot.ticks" :key="index" class="overlay-grid">
        <line x1="54" :x2="width-32" :y1="tickY(tick)" :y2="tickY(tick)" />
        <text x="46" :y="tickY(tick)+6" text-anchor="end">{{ compact(tick) }}</text>
      </g>
      <line v-if="variant!=='line'" x1="54" :x2="width-32" :y1="plot.zeroY" :y2="plot.zeroY" class="chart-zero-line" />
      <line v-if="readingX!==undefined" :x1="readingX" :x2="readingX" y1="28" y2="208" class="chart-inspection-line" />
      <g v-for="(line,index) in plot.series" :key="line.code" :class="`series-tone-${index}`">
        <path v-for="(path,segment) in variant!=='bars' ? line.areaPaths : []" :key="`area-${segment}`" :d="path" :fill="`url(#${gradientId}-${index})`" class="chart-area-fill" />
        <template v-if="variant==='bars'">
          <rect v-for="point in line.points" :key="point.period" :x="point.x-plot.barWidth/2" :y="Math.min(point.y,plot.zeroY)" :width="plot.barWidth" :height="Math.abs(point.y-plot.zeroY)" :rx="Math.min(4,Math.abs(point.y-plot.zeroY)/2)" :class="{'chart-bar--negative':point.value<0,'chart-bar--active':reading.period===point.period}" class="chart-bar"
            role="img" :aria-label="`${sectionPeriod(point.period,metricId)}: ${formatValue(point.value,unit)} ${unitLabel(unit)}`" @mouseenter="active=point.period" @click="active=point.period" />
        </template>
        <path v-else :d="line.path" fill="none" stroke="currentColor" stroke-width="3" :stroke-dasharray="patterns[index]" class="chart-series-line" />
        <circle v-for="point in line.points" :key="`point-${point.period}`" :cx="point.x" :cy="point.y" :r="reading.period===point.period ? 5 : variant==='bars' ? 2.5 : 3.5" :fill="index%2 ? 'var(--surface)' : variant==='bars' && point.value<0 ? 'var(--accent)' : 'currentColor'" :stroke="variant==='bars' && point.value<0 ? 'var(--accent)' : 'currentColor'" stroke-width="2"
          role="img" :aria-label="`${line.name}, ${sectionPeriod(point.period,metricId)}: ${formatValue(point.value,unit)} ${unitLabel(unit)}`"
          @mouseenter="active=point.period" @focus="active=point.period" @click="active=point.period" @blur="active=''" />
      </g>
      <text v-for="tick in ticks" :key="tick.period" :x="tick.x" y="248" text-anchor="middle" class="overlay-date">{{ sectionPeriod(tick.period,metricId).replace(' · anno scolastico','') }}</text>
    </svg>
    <figcaption class="overlay-reading" aria-live="polite">
      <span class="reading-period">{{ reading.period ? sectionPeriod(reading.period,metricId) : 'Nessun periodo utile' }}</span>
      <span v-for="(row,index) in reading.rows" :key="row.name" :class="`series-tone-${index}`"><i :class="`series-symbol-${index}`" />{{ series.length>1 ? row.name+': ' : '' }}<strong>{{ row.point?.status==='observed' ? formatValue(row.point.value,unit) : '—' }}</strong> {{ unitLabel(unit) }}</span>
    </figcaption>
    <p class="visual-note">{{ variant==='bars' ? 'Le barre partono da zero; quelle sotto lo zero sono color terracotta.' : variant==='area' ? 'Il grafico parte da zero.' : 'La scala verticale è adattata ai valori mostrati: non sempre parte da zero.' }} Gli anni sono distanziati in base al tempo trascorso. Dove il dato manca, il grafico si interrompe.</p>
  </figure>
</template>
