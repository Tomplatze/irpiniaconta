<script setup lang="ts">
import type { HealthPublication } from '../../../shared/health';
const props = defineProps<{ causes: HealthPublication['causes']; codes?: string[] }>();
const visibleCauses = computed(() => props.codes ? props.causes.filter(cause => props.codes!.includes(cause.code)) : props.causes);
const format = (value: number) => value.toLocaleString('it-IT');
/** Return a scale ceiling large enough to leave room above the largest column. */
function ceiling(values: number[]): number {
  const max = Math.max(...values);
  const step = max >= 1000 ? 500 : 50;
  return Math.ceil((max * 1.05) / step) * step;
}
</script>
<template>
  <div class="causes-grid"><article v-for="cause in visibleCauses" :key="cause.code" class="cause-chart"><header><div><p>Provincia di Avellino · 2018–2023</p><h3>{{ cause.name }}</h3></div><div class="cause-chart__latest"><strong>{{ format(cause.points.at(-1)?.value ?? 0) }}</strong><span>decessi nel 2023</span></div></header><div class="cause-chart__plot" :aria-label="`${cause.name}: decessi annuali dal 2018 al 2023`"><div class="cause-chart__ceiling">{{ format(ceiling(cause.points.map(p => p.value))) }}</div><div class="cause-chart__bars"><div v-for="point in cause.points" :key="point.year" class="cause-chart__column"><span class="cause-chart__value">{{ format(point.value) }}</span><div class="cause-chart__bar-space"><i :class="{'is-latest':point.year === 2023}" :style="{height:`${point.value / ceiling(cause.points.map(p => p.value)) * 100}%`}" /></div><span class="cause-chart__year">{{ point.year }}</span></div></div><div class="cause-chart__zero">0</div></div><p class="cause-chart__note">Numero di decessi · scala 0–{{ format(ceiling(cause.points.map(p => p.value))) }}</p></article></div>
</template>
<style scoped>
.causes-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.cause-chart{border:1px solid var(--line);border-radius:10px;background:#f8f8f1;padding:26px}.cause-chart header{display:flex;justify-content:space-between;gap:16px;min-height:90px}.cause-chart h3{font-size:clamp(18px,2vw,24px);line-height:1.2;margin:7px 0}.cause-chart header p,.cause-chart__note,.cause-chart__latest span{font-size:11px;color:var(--muted);line-height:1.4}.cause-chart__latest{display:flex;flex-direction:column;text-align:right;flex:none}.cause-chart__latest strong{font-size:34px;line-height:1.1;letter-spacing:-.05em;color:#b95f3e}.cause-chart__plot{height:185px;position:relative;padding:0 0 0 27px}.cause-chart__ceiling,.cause-chart__zero{position:absolute;left:0;font-size:10px;color:var(--muted)}.cause-chart__ceiling{top:16px}.cause-chart__zero{bottom:24px}.cause-chart__bars{height:100%;display:grid;grid-template-columns:repeat(6,1fr);gap:6px;align-items:end}.cause-chart__column{height:100%;display:flex;flex-direction:column;align-items:center;justify-content:end;min-width:0}.cause-chart__value{font-size:10px;font-weight:700;margin-bottom:4px;font-variant-numeric:tabular-nums}.cause-chart__bar-space{height:135px;width:100%;display:flex;align-items:end;justify-content:center;border-bottom:1px solid #9eb09f;background:linear-gradient(to bottom,transparent 49.5%,#e1e8df 50%,transparent 50.5%)}.cause-chart__bar-space i{display:block;width:min(75%,42px);background:#a6c0aa;border-radius:4px 4px 0 0}.cause-chart__bar-space i.is-latest{background:#cc704b}.cause-chart__year{height:19px;padding-top:4px;font-size:10px;color:var(--muted)}.cause-chart__note{margin:14px 0 0}@media(max-width:700px){.causes-grid{grid-template-columns:1fr}.cause-chart{padding:20px}}
</style>
