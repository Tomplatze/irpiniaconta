<script setup lang="ts">
import type { HealthPublication } from '../../../shared/health';
const props = defineProps<{ groups: HealthPublication['cancer'] }>();
const fmt = (n: number) => n.toLocaleString('it-IT', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
</script>
<template>
  <div class="cancer-overview"><div v-for="group in groups" :key="group.label" class="cancer-panel"><h3>{{ group.label }}</h3><p>ASL Avellino · incidenza 2020–2022</p><ol><li v-for="entry in group.entries" :key="entry.name"><div class="cancer-row"><span>{{ entry.name }}</span><strong>{{ fmt(entry.value) }}</strong></div><div class="cancer-plot" aria-hidden="true"><span class="cancer-bar" :style="{width: `${entry.value / 130 * 100}%`}"/><span class="cancer-interval" :style="{left: `${entry.low / 130 * 100}%`, width: `${(entry.high-entry.low) / 130 * 100}%`}" /></div><small>Intervallo di confidenza 95%: {{ fmt(entry.low) }}–{{ fmt(entry.high) }}</small></li></ol><div class="cancer-scale"><span>0</span><span>65</span><span>130</span></div></div></div>
</template>
<style scoped>
.cancer-overview{display:grid;grid-template-columns:1fr 1fr;gap:16px}.cancer-panel{border:1px solid var(--line);border-radius:10px;background:var(--surface);padding:28px}.cancer-panel h3{font-size:24px;line-height:1.2;margin:0}.cancer-panel>p,.cancer-panel small{color:var(--muted);font-size:12px}.cancer-panel ol{list-style:none;padding:0;margin:24px 0}.cancer-panel li{margin:20px 0}.cancer-row{display:flex;gap:10px;justify-content:space-between;font-size:13px}.cancer-plot{position:relative;height:10px;background:#e4e9dd;border-radius:8px;margin:8px 0 2px}.cancer-bar{display:block;height:100%;background:#d87a55;border-radius:8px}.cancer-interval{position:absolute;top:2px;height:6px;border-left:2px solid #294e3e;border-right:2px solid #294e3e;background:#294e3e}.cancer-scale{display:flex;justify-content:space-between;color:var(--muted);font-size:11px}@media(max-width:700px){.cancer-overview{grid-template-columns:1fr}.cancer-panel{padding:22px}}
</style>
