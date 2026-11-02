<script setup lang="ts">
import type { TerritoryMetric } from '../../../shared/sections';
import { formatValue, unitLabel } from '../../utils/presentation';
import { useChartWidth } from '../../composables/useChartWidth';
const props = defineProps<{ metric: TerritoryMetric }>();
const figure = ref<HTMLElement | null>(null);
const width = useChartWidth(figure);
const activeCode = ref('');
watch(()=>props.metric.series.map(item=>item.code).join(','),()=>{ activeCode.value=''; });
const comparing = computed(() => props.metric.series.length>1);
const measured = computed(() => props.metric.distribution.filter(row => row.status==='observed' && row.value!==null));
const selected = computed(() => props.metric.series.map((item,index)=>({...item,index})).filter(item=>item.code && item.current.status==='observed' && item.current.value!==null));
const domain = computed(() => comparing.value ? selected.value.map(item=>item.current.value!) : measured.value.map(row=>row.value!));
const low = computed(() => Math.min(0,...domain.value));
const high = computed(() => Math.max(0,...domain.value));
const x = (value: number): number => 16+(value-low.value)/(high.value-low.value || 1)*(width.value-32);
const reading = computed(() => props.metric.distribution.find(row=>row.code===activeCode.value));
const leaders = computed(() => [...measured.value].sort((a,b)=>b.value!-a.value! || a.name.localeCompare(b.name,'it')).slice(0,3));
/** One tab stop per graphic; arrow keys inspect values without traversing 118 tab stops. */
function step(direction: number): void {
  const rows = comparing.value ? measured.value.filter(row=>selected.value.some(item=>item.code===row.code)) : measured.value;
  const index = rows.findIndex(row=>row.code===activeCode.value);
  const next = index<0 ? (direction<0 ? rows.length-1 : 0) : (index+direction+rows.length)%rows.length;
  activeCode.value=rows[next]?.code ?? '';
}
</script>
<template>
  <figure ref="figure" class="latest-distribution">
    <svg :viewBox="`0 0 ${width} 156`" role="group" tabindex="0" :aria-label="`${metric.label}. ${unitLabel(metric.unit)}. ${comparing ? 'Comuni selezionati sullo stesso asse.' : 'Un punto per comune.'} Frecce destra e sinistra per leggere i valori.`" @keydown.left.prevent="step(-1)" @keydown.right.prevent="step(1)" @mouseleave="activeCode=''">
      <line x1="16" :x2="width-16" y1="80" y2="80" class="distribution-axis" />
      <line :x1="x(0)" :x2="x(0)" y1="28" y2="96" class="distribution-zero" />
      <circle v-for="row in comparing ? [] : measured" :key="row.code" :cx="x(row.value!)" cy="80" :r="activeCode===row.code ? 8 : 5" class="distribution-point"
        role="img" :aria-label="`${row.name}: ${formatValue(row.value,metric.unit)} ${unitLabel(metric.unit)}`"
        @focus="activeCode=row.code" @mouseenter="activeCode=row.code" @click="activeCode=row.code" @blur="activeCode=''" />
      <g v-for="item in selected" :key="item.code ?? item.index" :class="`series-tone-${item.index}`" @mouseenter="activeCode=item.code ?? ''" @click="activeCode=item.code ?? ''">
        <line :x1="x(item.current.value!)" :x2="x(item.current.value!)" :y1="32-item.index*5" y2="80" stroke="currentColor" stroke-width="2" :stroke-dasharray="item.index%2 ? '4 3' : undefined" />
        <circle :cx="x(item.current.value!)" :cy="32-item.index*5" r="7" :fill="item.index%2 ? 'var(--surface)' : 'currentColor'" stroke="currentColor" stroke-width="3" />
      </g>
      <text x="16" y="126">{{ formatValue(low,metric.unit) }}</text><text :x="width-16" y="126" text-anchor="end">{{ formatValue(high,metric.unit) }} {{ unitLabel(metric.unit) }}</text>
    </svg>
    <figcaption class="distribution-reading" aria-live="polite"><template v-if="reading"><strong>{{ reading.name }}</strong> · {{ formatValue(reading.value,metric.unit) }} {{ unitLabel(metric.unit) }}</template><template v-else>{{ comparing ? `${selected.length}/${metric.series.length} comuni selezionati con dato` : `Un punto per comune · ${measured.length}/118 con dato` }} · asse da zero</template></figcaption>
    <div v-if="!metric.series[0]?.code" class="leader-preview"><p class="visual-note">I tre valori più alti · stesso periodo</p><div v-for="row in leaders" :key="row.code"><span>{{ row.name }}</span><strong>{{ formatValue(row.value,metric.unit) }} {{ unitLabel(metric.unit) }}</strong><span class="leader-track"><i :style="{left:`${(Math.min(0,row.value!)-low)/(high-low || 1)*100}%`,width:`${Math.abs(row.value!)/(high-low || 1)*100}%`}" /></span></div></div>
  </figure>
</template>
