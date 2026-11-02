<script setup lang="ts">
import InterfaceIcon from '~/components/atoms/InterfaceIcon.vue';
import type { TerritoryMetric } from '../../../shared/sections';
import CategoryRadar from '../molecules/CategoryRadar.vue';
import TopicIllustration from '../atoms/TopicIllustration.vue';

const props = defineProps<{ metric: TerritoryMetric; kind: 'livestock' | 'organic' }>();
const definitions = {
  livestock: [
    { title: 'Bovini, bufalini, equini e ovini', ids: ['cattle', 'buffalo', 'horses', 'sheep'] },
    { title: 'Caprini, suini, avicoli e conigli', ids: ['goats', 'pigs', 'poultry', 'rabbits'] },
  ],
  organic: [
    { title: 'Vigneti, oliveti e frutteti', ids: ['vines', 'olives', 'fruit', 'citrus'] },
    { title: 'Cereali, legumi e ortaggi', ids: ['cereals', 'pulses', 'potatoes', 'vegetables'] },
    { title: 'Prati e altre coltivazioni', ids: ['temporary_grass', 'permanent_grass', 'industrial', 'other'] },
  ],
} as const;
const groups = computed(() => definitions[props.kind].map(group => {
  const entries = group.ids.map(id => props.metric.breakdown?.find(entry => entry.metric.id === `breakdown_${props.kind}_${id}`)).filter(entry => entry !== undefined);
  const values = entries.flatMap(entry => entry.series.map(item => item.current)).filter(item => item.status === 'observed' && item.value !== null && Number.isFinite(item.value) && item.value >= 0);
  return { title: group.title, entries, maximum: Math.max(0, ...values.map(item => item.value!)) };
}).filter(group => group.entries.length === 4));
</script>

<template>
  <section v-if="groups.length" class="crop-profiles" :aria-labelledby="`${kind}-profiles-title`">
    <header class="crop-profiles__header">
      <div class="crop-profiles__heading"><TopicIllustration topic="agriculture" :metric="kind === 'livestock' ? 'agricultural_holdings' : 'utilised_agricultural_area'" /><div><p class="eyebrow">Censimento agricolo 2020</p><h3 :id="`${kind}-profiles-title`">{{ kind === 'livestock' ? 'Gli allevamenti, specie per specie' : 'Le coltivazioni biologiche, da vicino' }}</h3></div></div>
      <p v-if="kind === 'livestock'">Gli animali sono attribuiti alla sede dell’azienda. Il dato sugli avicoli segue il periodo di riferimento indicato dalla fonte.</p>
      <p v-else>Le superfici sono attribuite alla sede dell’azienda. Alcune categorie possono comprendere altre colture: i valori non vanno sommati.</p>
    </header>
    <p class="crop-profiles__legend">Un dato non disponibile non equivale a zero.</p>
    <div class="crop-profiles__grid">
      <article v-for="group in groups" :key="group.title" class="crop-profile-card">
        <header><h4>{{ group.title }}</h4><span>{{ kind === 'livestock' ? 'Animali · capi' : 'Superficie · ettari' }}</span></header>
        <CategoryRadar :title="group.title" :entries="group.entries" :maximum="group.maximum" />
      </article>
    </div>
    <p class="crop-profiles__note">Dove il dato manca, il disegno si interrompe. Per l’Irpinia è indicato il numero di comuni con dati disponibili; la scala cambia tra i gruppi. <a v-if="metric.breakdown?.[0]?.metric.sources[0]" :href="metric.breakdown[0].metric.sources[0]!.url" target="_blank" rel="noreferrer">Fonte: ISTAT, censimento agricolo <InterfaceIcon name="arrow-up-right" /></a></p>
  </section>
</template>
