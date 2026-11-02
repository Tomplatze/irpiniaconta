<script setup lang="ts">
import { percentageCells } from '../../utils/metricVisuals';
import { formatValue } from '../../utils/presentation';
const props = defineProps<{ value: number | null; status: string; soil?: boolean; median?: boolean }>();
const cells = computed(() => props.status === 'observed' ? percentageCells(props.value) : null);
const ring = computed(() => cells.value ? cells.value.reduce((sum,value)=>sum+value,0) : null);
</script>
<template>
  <figure v-if="cells" class="percentage-visual" :class="{'percentage-visual--ring':!soil}">
    <div v-if="soil" class="percentage-waffle" role="img" :aria-label="`${formatValue(value)} su 100${median ? ', valore mediano comunale' : ''}. La parte colorata rappresenta la percentuale.`"><span v-for="(fraction,index) in cells" :key="index"><i :style="{width:`${fraction*100}%`}" /></span></div>
    <svg v-else viewBox="0 0 210 210" class="percentage-ring" role="img" :aria-label="`${formatValue(value)} per cento${median ? ', valore mediano comunale' : ''}. La circonferenza intera rappresenta 100.`">
      <circle cx="105" cy="105" r="78" class="percentage-ring-track" />
      <circle cx="105" cy="105" r="78" pathLength="100" :stroke-dasharray="`${ring} ${100-(ring ?? 0)}`" transform="rotate(-90 105 105)" class="percentage-ring-value" />
      <circle cx="105" cy="105" r="58" class="percentage-ring-inner" />
      <text x="105" y="107" text-anchor="middle" class="percentage-ring-label">{{ formatValue(value) }}<tspan class="percentage-ring-unit">%</tspan></text>
      <text x="105" y="130" text-anchor="middle" class="percentage-ring-denominator">su 100</text>
    </svg>
    <figcaption v-if="soil"><strong>{{ formatValue(value) }} m² artificiali ogni 100 m²</strong><span>{{ median ? 'È il valore centrale tra i comuni con dato, non la percentuale dell’intera provincia.' : 'Nel territorio del comune selezionato.' }}</span></figcaption>
    <figcaption v-else><strong>{{ formatValue(value) }} su 100</strong><span>{{ median ? 'È il valore centrale tra i comuni con dato.' : 'La parte colorata rappresenta la percentuale indicata.' }} L’anello completo vale 100%.</span><span class="percentage-ring-key"><i /> Percentuale indicata</span></figcaption>
  </figure>
</template>
