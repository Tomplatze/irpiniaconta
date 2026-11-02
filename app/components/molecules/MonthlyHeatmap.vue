<script setup lang="ts">
import { buildMonthlyCalendar, type OverlayInput } from '../../utils/history';
import { formatValue, unitLabel, statusLabel } from '../../utils/presentation';
import { sectionPeriod } from '../../utils/sections';
const props = defineProps<{ series: OverlayInput[]; unit: string; label: string; metricId: string }>();
const calendar = computed(() => buildMonthlyCalendar(props.series[0]?.values ?? []));
const active = ref('');
const selected = computed(() => calendar.value.cells.find(cell => cell.period===active.value) ?? calendar.value.cells.at(-1));
watch(() => props.series, () => { active.value=''; });

/** Relative temperature shading encodes the observed annual range, never a target or anomaly. */
function shade(fraction: number | null): string {
  if (fraction===null) return 'var(--soft)';
  return `color-mix(in srgb, #dfac91 ${Math.round(fraction*100)}%, #d3e1cc)`;
}
</script>
<template>
  <figure v-if="calendar.cells.length" class="monthly-heatmap" :aria-label="`${label}, ${calendar.year}`">
    <div class="monthly-calendar" role="group" :aria-label="`Temperature mensili ${calendar.year}. Ogni riquadro è un mese.`">
      <button v-for="cell in calendar.cells" :key="cell.period" type="button" class="month-cell" :class="{'month-cell--missing':cell.fraction===null,'month-cell--active':selected?.period===cell.period}" :style="{'--month-color':shade(cell.fraction)}"
        :aria-label="`${sectionPeriod(cell.period,metricId)}: ${cell.status==='observed' ? formatValue(cell.value,unit)+' '+unitLabel(unit) : statusLabel(cell.status)}`" :aria-pressed="selected?.period===cell.period" @mouseenter="active=cell.period" @focus="active=cell.period" @click="active=cell.period">
        <span class="month-label">{{ cell.label }}</span><strong>{{ cell.status==='observed' ? formatValue(cell.value,unit) : '—' }}</strong><span class="month-unit">{{ unitLabel(unit) }}</span>
      </button>
    </div>
    <figcaption>
      <p class="monthly-inspection" aria-live="polite"><span>{{ selected ? sectionPeriod(selected.period,metricId) : calendar.year }}</span><strong>{{ selected?.status==='observed' ? formatValue(selected.value,unit)+' '+unitLabel(unit) : statusLabel(selected?.status ?? 'missing') }}</strong></p>
      <div v-if="calendar.minimum!==null && calendar.maximum!==null" class="monthly-temperature-key"><span>{{ formatValue(calendar.minimum,unit) }} {{ unitLabel(unit) }}</span><i aria-hidden="true" /><span>{{ formatValue(calendar.maximum,unit) }} {{ unitLabel(unit) }}</span></div>
      <p class="visual-note">Medie mensili del {{ calendar.year }}. Colori dal mese più fresco al più caldo della serie; i mesi senza dato restano vuoti.</p>
    </figcaption>
  </figure>
</template>
