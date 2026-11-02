<script setup lang="ts">
import InterfaceIcon from '~/components/atoms/InterfaceIcon.vue';
import type { TerritoryMetric } from '../../../shared/sections';
import CategoryRadar from '../molecules/CategoryRadar.vue';
import TopicIllustration from '../atoms/TopicIllustration.vue';
const props = defineProps<{ metric: TerritoryMetric }>();
const definitions = [
  {title:'Colture legnose e fruttiferi', ids:['viney','oliv','fruit','agrcult']},
  {title:'Cereali, legumi e ortaggi', ids:['cereals','drpul','potat','vegfr']},
  {title:'Prati, pascoli e altri terreni', ids:['pgrapm','tgra','falland','kitgar']},
  {title:'Altre colture dei seminativi', ids:['cropin','beets','fodr','seedl_seeds']},
  {title:'Colture protette e vivai', ids:['arland_vegco','pcrog','nurse','flow']},
] as const;
const groups = computed(() => definitions.map(group => {
  const entries = group.ids.map(id => props.metric.breakdown?.find(entry => entry.metric.id === `breakdown_crops_${id}`)).filter(entry => entry !== undefined);
  const observed = entries.flatMap(entry => entry.series.map(item => item.current)).filter(item => item.status === 'observed' && item.value !== null && Number.isFinite(item.value) && item.value >= 0);
  return {title:group.title, entries, maximum:Math.max(0, ...observed.map(item => item.value!))};
}).filter(group => group.entries.length === 4));
</script>
<template>
  <section v-if="groups.length" class="crop-profiles" aria-labelledby="crop-profiles-title">
    <header class="crop-profiles__header"><div class="crop-profiles__heading"><TopicIllustration topic="agriculture" metric="utilised_agricultural_area" /><div><p class="eyebrow">Censimento agricolo {{ metric.breakdown?.[0]?.metric.latest_period }}</p><h3 id="crop-profiles-title">Le coltivazioni, da vicino</h3></div></div><p>Le superfici sono attribuite alla sede dell’azienda. Alcune categorie ne comprendono altre: i valori non vanno sommati.</p></header>
    <p class="crop-profiles__legend"><strong aria-hidden="true">—</strong> Dato non disponibile, non valido o riservato: non equivale a zero.</p>
    <div class="crop-profiles__grid">
      <article v-for="group in groups" :key="group.title" class="crop-profile-card">
        <header><h4>{{ group.title }}</h4><span>Superficie · ettari</span></header>
        <CategoryRadar :title="group.title" :entries="group.entries" :maximum="group.maximum" />
      </article>
    </div>
    <p class="crop-profiles__note">Un dato mancante non significa zero: il disegno si interrompe. È indicato quanti comuni hanno dati disponibili; la scala cambia tra i gruppi. <a v-if="metric.breakdown?.[0]?.metric.sources[0]" :href="metric.breakdown[0].metric.sources[0]!.url" target="_blank" rel="noreferrer">Fonte: ISTAT, censimento agricolo <InterfaceIcon name="arrow-up-right" /></a></p>
  </section>
</template>
