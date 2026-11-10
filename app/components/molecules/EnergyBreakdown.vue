<script setup lang="ts">
const props = defineProps<{
  title: string;
  items: { label: string; value: number | null; color: string }[];
  variant: 'donut' | 'bars';
}>();

const measuredTotal = computed(() => props.items.reduce((sum, item) => sum + (item.value ?? 0), 0));
const ranked = computed(() => [...props.items].sort((a, b) => (b.value ?? -1) - (a.value ?? -1)));

/** Use the sum of displayed categories for the composition, keeping Terna's rounded total separate. */
function share(value: number | null): number {
  return measuredTotal.value > 0 ? (value ?? 0) / measuredTotal.value * 100 : 0;
}

const fill = computed(() => {
  let start = 0;
  const stops = ranked.value.filter(item => (item.value ?? 0) > 0).map(item => {
    const end = start + share(item.value);
    const stop = `${item.color} ${start}% ${end}%`;
    start = end;
    return stop;
  });
  return stops.length ? `conic-gradient(${stops.join(',')})` : 'var(--soft)';
});
const leading = computed(() => ranked.value[0]);
const percent = new Intl.NumberFormat('it-IT', { maximumFractionDigits: 0 });
const amount = new Intl.NumberFormat('it-IT', { useGrouping: true, maximumFractionDigits: 1 });
</script>

<template>
  <section class="energy-breakdown">
    <h4>{{ title }}</h4>
    <div class="energy-breakdown-body" :class="{ 'energy-breakdown-body--donut': variant === 'donut' }">
      <div v-if="variant === 'donut' && measuredTotal > 0 && leading" class="energy-donut">
        <div class="energy-donut-ring" :style="{ background: fill }" aria-hidden="true"></div>
        <div class="energy-donut-center">
          <strong>{{ percent.format(share(leading.value)) }}%</strong>
          <span>{{ leading.label }}</span>
        </div>
      </div>
      <ul>
        <li v-for="item in ranked" :key="item.label" :style="{ '--item-color': item.color }">
          <span class="energy-item-label"><i v-if="variant === 'donut' && item.value !== null" aria-hidden="true"></i>{{ item.label }}</span>
          <strong>{{ item.value === null ? '—' : amount.format(item.value) + ' GWh' }}</strong>
          <span v-if="variant === 'bars' && item.value !== null" class="energy-track" aria-hidden="true">
            <span :style="{ width: `${share(item.value)}%` }" />
          </span>
        </li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.energy-breakdown { min-width: 0; }
.energy-breakdown h4 { margin: 0 0 1rem; font-size: 1rem; }
.energy-breakdown-body--donut { display: flex; flex-wrap: wrap; align-items: center; gap: 1.25rem; }
.energy-donut { position: relative; display: grid; place-items: center; width: 7.5rem; aspect-ratio: 1; flex: 0 0 auto; }
.energy-donut-ring { position: absolute; inset: 0; border-radius: 50%; }
.energy-donut-center {
  position: relative;
  display: grid;
  align-content: center;
  justify-items: center;
  width: 73%;
  aspect-ratio: 1;
  border-radius: 50%;
  background: var(--surface);
  text-align: center;
}
.energy-donut-center strong { font-size: 1.55rem; line-height: 1.15; }
.energy-donut-center span { font-size: .75rem; color: var(--muted); }
ul { list-style: none; display: grid; gap: .6rem; margin: 0; padding: 0; flex: 1 1 9rem; }
li { display: grid; grid-template-columns: 1fr auto; gap: .25rem .65rem; font-size: .85rem; align-items: baseline; }
li strong { font-variant-numeric: tabular-nums; white-space: nowrap; }
.energy-item-label { display: flex; align-items: center; gap: .45rem; }
.energy-item-label i { width: .55rem; height: .55rem; flex: 0 0 auto; border-radius: 50%; background: var(--item-color); }
.energy-track { grid-column: 1 / -1; display: block; height: .4rem; border-radius: .5rem; background: var(--soft); }
.energy-track span { display: block; height: 100%; border-radius: inherit; background: var(--item-color); }
@media (max-width: 360px) {
  .energy-breakdown-body--donut { justify-content: center; }
}
</style>
