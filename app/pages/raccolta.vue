<script setup lang="ts">
import InterfaceIcon from '~/components/atoms/InterfaceIcon.vue';
import type { CollectionInventory, CollectionScope } from '../../shared/collection';
import type { SectionOverview } from '../../shared/sections';
import type { Catalogue } from '../../shared/catalogue';
import CollectionSourceCard from '../components/molecules/CollectionSourceCard.vue';
import EditorialHeader from '../components/molecules/EditorialHeader.vue';
import StatusBreakdown from '../components/molecules/StatusBreakdown.vue';
import TopicIllustration from '../components/atoms/TopicIllustration.vue';
import TopicNavigator from '../components/organisms/TopicNavigator.vue';
import { collectionStatusLabels, sourceGeography } from '../utils/sourcePresentation';
const { data: inventory, error } = await useFetch<CollectionInventory>('/api/collection');
const { data: catalogue, error: catalogueError } = await useFetch<Catalogue>('/api/catalogue');
const { data: sections } = await useFetch<SectionOverview>('/api/sections');
const route = useRoute();
const category = ref(typeof route.query.category === 'string' && inventory.value?.categories.some(item => item.id === route.query.category) ? route.query.category : 'all');
const state = ref('all');
const query = ref('');
const catalogueQuery = ref('');
const catalogueSources = computed(() => catalogue.value?.sources.filter(source =>
  `${source.title} ${source.publisher}`.toLocaleLowerCase('it-IT').includes(catalogueQuery.value.trim().toLocaleLowerCase('it-IT'))) ?? []);
const selectedSourceIds = computed(() => new Set(sections.value?.categories.flatMap(item => item.metrics.flatMap(metric => metric.sources.map(source => source.id))) ?? []));
const publishedDatasets: Record<string, string> = {
  'DEM-04': 'istat-foreign-age-2026',
  'AGR-03': 'istat-df_dcat_censagric2020_cattle_all',
  'AGR-06': 'istat-df_dcat_censagric2020_org_crops',
};
const assessedSources = computed<CollectionScope[]>(() => inventory.value?.sources.map(source => {
  const dataset = publishedDatasets[source.id];
  return dataset && source.dataset_ids.includes(dataset) && selectedSourceIds.value.has(dataset)
    ? { ...source, status: 'integrated' } : source;
}) ?? []);
const sources = computed(() => assessedSources.value.filter(source =>
  (category.value === 'all' || source.category_id === category.value)
  && (state.value === 'all' || source.status === state.value)
  && `${source.title} ${source.publisher} ${source.ui_summary}`.toLocaleLowerCase('it-IT').includes(query.value.trim().toLocaleLowerCase('it-IT'))));
const groups = computed(() => inventory.value?.categories.map(item => ({ ...item, sources: sources.value.filter(source => source.category_id === item.id) })).filter(item => item.sources.length) ?? []);
const statusItems = computed(() => (Object.keys(collectionStatusLabels) as CollectionScope['status'][]).map(id => ({ id, label: collectionStatusLabels[id], count: assessedSources.value.filter(source => source.status === id).length })));
useHead({ title: 'Dati e fonti — IrpiniaConta' });
useSeoMeta({ description: 'Scopri le fonti dei dati di IrpiniaConta, gli anni disponibili e i territori a cui si riferiscono.', ogTitle: 'Dati e fonti — IrpiniaConta', ogDescription: 'Scopri le fonti dei dati di IrpiniaConta, gli anni disponibili e i territori a cui si riferiscono.', twitterTitle: 'Dati e fonti — IrpiniaConta', twitterDescription: 'Scopri le fonti dei dati di IrpiniaConta, gli anni disponibili e i territori a cui si riferiscono.' });
</script>

<template>
  <div class="supporting-page collection-page">
    <EditorialHeader eyebrow="Dietro ogni numero, una fonte" title="Da dove arrivano" accent="i dati." description="Scopri chi pubblica i dati, a quali anni si riferiscono e per quanti comuni sono disponibili. Ogni indicatore rimanda alla propria fonte." topic="sources"><NuxtLink to="/">Esplora l’Irpinia <InterfaceIcon name="arrow-up-right" /></NuxtLink><a href="#catalogo-fonti">Catalogo delle fonti <InterfaceIcon name="arrow-down" /></a></EditorialHeader>
    <p v-if="error" class="notice" role="alert">Non riusciamo a mostrare le fonti. Riprova più tardi.</p>
    <template v-if="inventory">
      <div class="editorial-figures" aria-label="Stato della raccolta">
        <div><strong>{{ inventory.summary.scope_with_data_count }}<small>/{{ inventory.summary.scope_count }}</small></strong><span>voci con dati o fonti alternative</span></div>
        <div><strong>{{ inventory.summary.collected_dataset_families }}</strong><span>raccolte di dati verificate</span></div>
        <div v-if="sections"><strong>{{ sections.metric_count }}</strong><span>indicatori scelti per l’atlante</span></div>
      </div>
      <StatusBreakdown label="Disponibilità delle voci censite" :items="statusItems" />
      <p class="supporting-note">Una stessa fonte può comparire in più voci o riguardare più argomenti. Gli anni indicano a quando risalgono i dati; la presenza di una voce non garantisce che l’elenco sia completo.</p>
      <section id="catalogo-fonti" class="source-catalogue" aria-labelledby="source-catalogue-title">
        <header><div><p class="eyebrow">Le fonti consultate</p><h2 id="source-catalogue-title">Catalogo delle fonti</h2><p>Le fonti esaminate, comprese quelle i cui dati non sono ancora disponibili nell’atlante.</p></div></header>
        <p v-if="catalogueError" class="notice" role="alert">Non riusciamo a mostrare il catalogo. Riprova più tardi.</p>
        <details v-else-if="catalogue" class="source-catalogue__details">
          <summary>Consulta l’elenco completo · {{ catalogue.sources.length }} fonti</summary>
          <label>Cerca nel catalogo<input v-model="catalogueQuery" type="search" placeholder="Titolo o ente…"></label>
          <p class="source-catalogue__count" role="status">{{ catalogueSources.length }} {{ catalogueSources.length === 1 ? 'fonte' : 'fonti' }}</p>
          <ul class="source-catalogue__list">
            <li v-for="source in catalogueSources" :key="source.id">
              <div><a :href="source.landing_url" target="_blank" rel="noopener noreferrer">{{ source.title }} <InterfaceIcon name="arrow-up-right" /></a><span>{{ source.publisher }} · {{ sourceGeography(source.geography) }}</span></div>
            </li>
          </ul>
          <p v-if="!catalogueSources.length">Nessuna fonte trovata. Prova una ricerca diversa.</p>
        </details>
      </section>
      <form class="source-filters" role="search" aria-label="Filtra le fonti raccolte" @submit.prevent>
        <label>Tema<select v-model="category"><option value="all">Tutti i temi</option><option v-for="item in inventory.categories" :key="item.id" :value="item.id">{{ item.label }}</option></select></label>
        <label>Disponibilità<select v-model="state"><option value="all">Tutte</option><option v-for="(label,id) in collectionStatusLabels" :key="id" :value="id">{{ label }}</option></select></label>
        <label>Cerca una fonte<input v-model="query" type="search" placeholder="Redditi, clima, castelli…"></label>
      </form>
      <p class="filter-result" role="status">{{ sources.length }} {{ sources.length===1 ? 'voce' : 'voci' }} in {{ groups.length }} {{ groups.length===1 ? 'tema' : 'temi' }}</p>
      <TopicNavigator v-if="groups.length" :categories="groups" :order="inventory.categories.map(item => item.id)" />
      <section v-for="group in groups" :id="`tema-${group.id}`" :key="group.id" class="source-chapter" :aria-labelledby="`collection-${group.id}`">
        <header class="source-chapter-heading"><div><p class="eyebrow">{{ String(inventory.categories.findIndex(item => item.id === group.id) + 1).padStart(2,'0') }} · Le fonti del tema</p><h2 :id="`collection-${group.id}`">{{ group.label }}</h2></div><TopicIllustration :topic="group.id" /></header>
        <div class="collection-card-grid"><CollectionSourceCard v-for="source in group.sources" :key="source.id" :source="source" :datasets="inventory.datasets" /></div>
      </section>
      <p v-if="!sources.length" class="empty-state">Nessuna fonte corrisponde ai filtri. Prova un altro tema o una ricerca più breve.</p>
    </template>
  </div>
</template>
