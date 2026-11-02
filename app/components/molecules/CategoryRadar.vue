<script setup lang="ts">
import type { TerritoryMetric } from '../../../shared/sections';
import { formatValue, statusLabel, unitLabel } from '../../utils/presentation';
type Entry = NonNullable<TerritoryMetric['breakdown']>[number];
const props = defineProps<{ title: string; entries: Entry[]; maximum: number }>();
const points = computed<Array<readonly [number, number]>>(() => props.entries.length === 3 ? [[100, 8], [180, 146], [20, 146]] : [[100, 8], [192, 100], [100, 192], [8, 100]]);
const axisClasses = computed(() => props.entries.length === 3 ? ['crop-radar__label--top', 'crop-radar__label--right', 'crop-radar__label--left'] : ['crop-radar__label--top', 'crop-radar__label--right', 'crop-radar__label--bottom', 'crop-radar__label--left']);
const unit = computed(() => props.entries[0]?.metric.unit ?? '');
/** Use the singular for one local unit while retaining the source unit. */
function displayUnit(amount: number | null): string { return unit.value === 'local units' && amount === 1 ? 'unità locale' : unit.value === 'heads' && amount === 1 ? 'capo' : unitLabel(unit.value); }
const scopes = computed(() => props.entries[0]?.series ?? []);
/** Return only observed, finite non-negative measurements from the selected scope. */
function value(index: number, scope: number): number | null {
  const current = props.entries[index]?.series[scope]?.current;
  return current?.status === 'observed' && current.value !== null && Number.isFinite(current.value) && current.value >= 0 ? current.value : null;
}
/** The same group uses one scale across all selected territories. */
function position(index: number, fraction: number): [number, number] {
  const target = points.value[index]!;
  return [100 + (target[0] - 100) * fraction, 100 + (target[1] - 100) * fraction];
}
function point(index: number, scope: number): [number, number] | null {
  const observed = value(index, scope);
  return observed === null ? null : position(index, props.maximum > 0 ? observed / props.maximum : 0);
}
function polygon(fraction: number): string {
  return points.value.map((_, index) => position(index, fraction).join(',')).join(' ');
}
function contour(scope: number): string | null {
  if (props.entries.some((_, index) => value(index, scope) === null)) return null;
  return props.entries.map((_, index) => point(index, scope)!.join(',')).join(' ');
}
const hasObserved = computed(() => props.entries.some((_, index) => scopes.value.some((_, scope) => value(index, scope) !== null)));
</script>
<template>
  <figure class="crop-radar">
    <div class="crop-radar__layout">
      <div v-for="(entry, index) in entries" :key="entry.metric.id" class="crop-radar__label" :class="axisClasses[index]">
        <span class="crop-radar__axis-title">{{ entry.metric.label }}</span>
        <div v-for="(item, scope) in entry.series" :key="item.code ?? 'province'" class="crop-radar__value" :class="`crop-radar__value--${scope}`">
          <small v-if="scopes.length > 1">{{ item.name }}</small>
          <strong v-if="value(index, scope) !== null">{{ formatValue(value(index, scope), unit) + ' ' + displayUnit(value(index, scope)) }}</strong><strong v-else class="crop-radar__missing">{{ item.current.status === 'observed' ? 'Dato non valido' : statusLabel(item.current.status) }}</strong>
          <small v-if="item.code === null && value(index, scope) !== null">{{ item.current.coverage }}/118 comuni</small>
        </div>
      </div>
      <svg v-if="hasObserved" class="crop-radar__chart" viewBox="0 0 200 200" role="img" :aria-label="`${title}. Valori e territori indicati accanto a ciascun vertice.`">
        <polygon v-for="level in [0.25, 0.5, 0.75, 1]" :key="level" :points="polygon(level)" class="crop-radar__grid" />
        <line v-for="(target, index) in points" :key="`axis-${index}`" x1="100" y1="100" :x2="target[0]" :y2="target[1]" class="crop-radar__axis" />
        <g v-for="(item, scope) in scopes" :key="item.code ?? 'province'" :class="`crop-radar__series--${scope}`">
          <polygon v-if="contour(scope)" :points="contour(scope)!" class="crop-radar__fill" />
          <template v-for="(_, index) in entries" :key="`segment-${index}`">
            <line v-if="point(index, scope) && point((index + 1) % entries.length, scope)" :x1="point(index, scope)![0]" :y1="point(index, scope)![1]" :x2="point((index + 1) % entries.length, scope)![0]" :y2="point((index + 1) % entries.length, scope)![1]" class="crop-radar__line" />
            <circle v-if="point(index, scope)" :cx="point(index, scope)![0]" :cy="point(index, scope)![1]" r="3.5" class="crop-radar__point" />
          </template>
        </g>
      </svg>
      <p v-else class="crop-radar__empty">Nessun dato disponibile per i territori selezionati</p>
    </div>
    <p v-if="hasObserved" class="crop-radar__scale">{{ maximum === 0 ? 'Tutti i valori disponibili sono zero' : `Da 0 a ${formatValue(maximum, unit)} ${displayUnit(maximum)} · scala del gruppo` }}{{ scopes.length > 1 ? ', comune ai territori selezionati' : '' }}.</p>
  </figure>
</template>
