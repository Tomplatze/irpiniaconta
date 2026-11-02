<script setup lang="ts">
import type { TerritoryMetric } from '../../../shared/sections';
import CategoryRadar from '../molecules/CategoryRadar.vue';
import TopicIllustration from '../atoms/TopicIllustration.vue';
const props = defineProps<{ metric: TerritoryMetric }>();
const definitions = [
  {title:'Industria, energia e ambiente', ids:['b','c','d','e']},
  {title:'Commercio, trasporti e ospitalità', ids:['g','h','i']},
  {title:'Costruzioni, immobili e professioni', ids:['f','l','m']},
  {title:'Comunicazione e servizi alle imprese', ids:['j','k','n']},
  {title:'Istruzione, salute e altri servizi', ids:['p','q','r','s']},
] as const;
const groups = computed(() => definitions.map(group => {
  const entries = group.ids.map(id => props.metric.breakdown?.find(entry => entry.metric.id === `breakdown_asia_${id}`)).filter(entry => entry !== undefined);
  const observed = entries.flatMap(entry => entry.series.map(item => item.current)).filter(item => item.status === 'observed' && item.value !== null && Number.isFinite(item.value) && item.value >= 0);
  return {title:group.title,entries,maximum:Math.max(0,...observed.map(item => item.value!)),expected:group.ids.length};
}).filter(group => group.entries.length === group.expected));
</script>
<template>
  <section v-if="groups.length" class="crop-profiles economic-profiles" aria-labelledby="economic-profiles-title">
    <header class="crop-profiles__header"><div class="crop-profiles__heading"><TopicIllustration topic="economy" metric="asia_local_units" /><div><p class="eyebrow">Registro statistico ASIA · {{ metric.breakdown?.[0]?.metric.latest_period }}</p><h3 id="economic-profiles-title">Le attività, settore per settore</h3></div></div><p>Le sedi delle imprese sono raggruppate per tipo di attività, secondo la classificazione ufficiale ATECO.</p></header>
    <p class="crop-profiles__legend"><strong aria-hidden="true">—</strong> Dato non disponibile, non valido o riservato: non equivale a zero.</p>
    <div class="crop-profiles__grid">
      <article v-for="group in groups" :key="group.title" class="crop-profile-card">
        <header><h4>{{ group.title }}</h4><span>Unità locali</span></header>
        <CategoryRadar :title="group.title" :entries="group.entries" :maximum="group.maximum" />
      </article>
    </div>
    <p class="crop-profiles__note">Un dato mancante non significa zero: il disegno si interrompe. Per ogni settore è indicato quanti comuni hanno dati disponibili. La scala cambia tra i gruppi. <a v-if="metric.breakdown?.[0]?.metric.sources[0]" :href="metric.breakdown[0].metric.sources[0]!.url" target="_blank" rel="noreferrer">Fonte: ISTAT, registro ASIA ↗</a></p>
  </section>
</template>
