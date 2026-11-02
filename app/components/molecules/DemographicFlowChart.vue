<script setup lang="ts">
import InterfaceIcon from '~/components/atoms/InterfaceIcon.vue';
import type { DemographicFlow } from '../../../shared/demographicFlows';
import type { SectionPoint } from '../../../shared/sections';
import { useChartWidth } from '../../composables/useChartWidth';
import { buildDemographicFlowPlot, demographicFlowPeriodNote, observedFlowCount } from '../../utils/demographicFlowPlot';
import { formatValue, statusLabel } from '../../utils/presentation';
const props = defineProps<{flow: DemographicFlow; latestPeriod?: string}>();
const figure = ref<HTMLElement | null>(null);
const width = useChartWidth(figure);
const plot = computed(() => buildDemographicFlowPlot(props.flow,width.value));
const gradientId = `flow-fill-${useId().replaceAll(':','')}`;
const active = ref('');
const readingPeriod = computed(() => active.value || (props.latestPeriod && plot.value.periods.some(point => point.period === props.latestPeriod) ? props.latestPeriod : plot.value.periods.at(-1)?.period) || '');
const reading = computed(() => props.flow.series[0]?.values.find(point => point.period === readingPeriod.value));
const readingX = computed(() => plot.value.periods.find(point => point.period === readingPeriod.value)?.x);
const sourceNote = computed(() => demographicFlowPeriodNote(props.flow.period_notes[readingPeriod.value]));
const ticks = computed(() => {
  const periods = plot.value.periods;
  if (width.value < 440 && periods.length > 2) return [periods[0]!,periods.at(-1)!];
  return periods.length <= 5 ? periods : [periods[0]!,periods[Math.floor((periods.length - 1) / 2)]!,periods.at(-1)!];
});
const compact = (value: number): string => new Intl.NumberFormat('it-IT',{notation:'compact',maximumFractionDigits:1}).format(value);
const labels = computed(() => ({positive:props.flow.positive.label,negative:props.flow.negative.label}));
watch(() => props.flow, () => { active.value = ''; });

/** A single keyboard stop reads both components at the same source year. */
function step(direction: number): void {
  const periods = plot.value.periods;
  const index = periods.findIndex(point => point.period === readingPeriod.value);
  active.value = periods[Math.max(0,Math.min(periods.length - 1,index + direction))]?.period ?? '';
}
/** Inspect the nearest calendar position without inventing intermediate values. */
function inspectPointer(event: PointerEvent): void {
  const bounds = (event.currentTarget as SVGSVGElement).getBoundingClientRect();
  const x = (event.clientX - bounds.left) / bounds.width * width.value;
  active.value = plot.value.periods.reduce<{period: string; x: number} | undefined>((nearest,point) => !nearest || Math.abs(point.x - x) < Math.abs(nearest.x - x) ? point : nearest,undefined)?.period ?? '';
}
function countLabel(point: SectionPoint | undefined): string {
  const value = observedFlowCount(point);
  return value !== null ? formatValue(value,'persons') : point?.status === 'observed' ? 'Dato non valido' : statusLabel(point?.status ?? 'unavailable');
}
</script>
<template>
  <figure ref="figure" class="demographic-flow-chart" :class="`demographic-flow-chart--${flow.kind}`">
    <template v-if="plot.hasData">
    <div class="demographic-flow-legend" aria-hidden="true"><span class="flow-positive"><i /><InterfaceIcon v-if="flow.kind==='natural'" name="arrow-up" /> {{ flow.positive.label }}</span><span class="flow-negative"><i /><InterfaceIcon v-if="flow.kind==='natural'" name="arrow-down" /> {{ flow.negative.label }}</span></div>
    <svg :viewBox="`0 0 ${width} ${plot.height}`" role="group" tabindex="0" :aria-label="`${flow.positive.label} e ${flow.negative.label} negli anni. Conteggi di persone. ${flow.kind==='natural' ? 'Nati sopra lo zero e morti sotto lo zero, entrambi come conteggi positivi.' : 'Due linee di conteggi annuali sulla stessa scala da zero.'} Usa le frecce destra e sinistra per leggere entrambi i valori nello stesso anno.`" @pointermove="inspectPointer" @pointerleave="active=''" @keydown.left.prevent="step(-1)" @keydown.right.prevent="step(1)" @keydown.home.prevent="active=plot.periods[0]?.period ?? ''" @keydown.end.prevent="active=plot.periods.at(-1)?.period ?? ''">
      <defs><linearGradient v-for="component in plot.components" :id="`${gradientId}-${component.id}`" :key="component.id" :class="`flow-${component.id}`" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="currentColor" stop-opacity=".12" /><stop offset="100%" stop-color="currentColor" stop-opacity=".025" /></linearGradient></defs>
      <g v-for="(tick,index) in plot.ticks" :key="index" class="demographic-flow-grid"><line :x1="plot.left" :x2="plot.right" :y1="tick.y" :y2="tick.y" /><text :x="plot.left - 9" :y="tick.y + 4" text-anchor="end">{{ compact(tick.value) }}</text></g>
      <line :x1="plot.left" :x2="plot.right" :y1="plot.zeroY" :y2="plot.zeroY" class="demographic-flow-zero" />
      <line v-if="readingX!==undefined" :x1="readingX" :x2="readingX" :y1="plot.top" :y2="plot.bottom" class="demographic-flow-inspector" />
      <g v-for="component in plot.components" :key="component.id" :class="`flow-${component.id}`">
        <path v-for="(path,index) in flow.kind==='natural' ? [] : component.areaPaths" :key="`area-${index}`" :d="path" :fill="`url(#${gradientId}-${component.id})`" class="chart-area-fill" />
        <template v-if="flow.kind==='natural'"><rect v-for="point in component.points" :key="point.period" :x="point.x - plot.barWidth/2" :y="Math.min(point.y,plot.zeroY)" :width="plot.barWidth" :height="Math.abs(point.y - plot.zeroY)" :rx="Math.min(3,Math.abs(point.y - plot.zeroY)/2)" class="demographic-flow-bar" :class="{'demographic-flow-bar--active':point.period===readingPeriod}" aria-hidden="true" /></template>
        <path v-else :d="component.path" fill="none" stroke="currentColor" stroke-width="3" :stroke-dasharray="component.id==='negative' ? '8 5' : undefined" class="demographic-flow-line" />
        <circle v-for="point in component.points" :key="`point-${point.period}`" :cx="point.x" :cy="point.y" :r="point.period===readingPeriod ? 4.5 : 3" :fill="component.id==='negative' ? 'var(--surface)' : 'currentColor'" stroke="currentColor" stroke-width="2" role="img" :aria-label="`${point.period}, ${labels[component.id]}: ${formatValue(point.value,'persons')} persone`" />
      </g>
      <text v-for="tick in ticks" :key="tick.period" :x="tick.x" y="278" text-anchor="middle" class="demographic-flow-year">{{ tick.period }}</text>
    </svg>
    <figcaption class="demographic-flow-reading" aria-live="polite" aria-atomic="true"><span class="demographic-flow-period">{{ readingPeriod }}</span><span class="flow-positive"><i aria-hidden="true" />{{ flow.positive.label }} <strong>{{ countLabel(reading?.positive) }}</strong></span><span class="flow-negative"><i aria-hidden="true" />{{ flow.negative.label }} <strong>{{ countLabel(reading?.negative) }}</strong></span></figcaption>
    <p v-if="sourceNote" class="demographic-flow-source-note">{{ sourceNote }}</p>
    <p class="visual-note">{{ flow.kind==='natural' ? 'I nati sono sopra lo zero e i morti sotto: i numeri indicano sempre persone.' : 'Le due linee mostrano separatamente arrivi e partenze, con la stessa scala.' }} La distanza tra gli anni rispecchia il tempo trascorso. I dati mancanti restano vuoti.</p>
    </template>
    <p v-else class="visual-note">Lo storico dei due flussi non è disponibile per il territorio selezionato.</p>
  </figure>
</template>
