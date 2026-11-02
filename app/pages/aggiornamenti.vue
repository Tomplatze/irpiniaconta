<script setup lang="ts">
import InterfaceIcon from '~/components/atoms/InterfaceIcon.vue';
import type { RunSummary, Catalogue } from '../../shared/catalogue';
import EditorialHeader from '../components/molecules/EditorialHeader.vue';
import SourceList from '../components/organisms/SourceList.vue';
import { formatDate } from '../utils/presentation';
import { sourceStatusLabels } from '../utils/sourcePresentation';
if (!import.meta.dev) throw createError({ statusCode: 404, statusMessage: 'Pagina non trovata' });
const { data: runs, error: runsError } = await useFetch<RunSummary[]>('/api/updates');
const { data: catalogue, error: catalogueError } = await useFetch<Catalogue>('/api/catalogue');
const showAll = ref(false);
const state = ref('all');
const query = ref('');
const visibleRuns = computed(() => showAll.value ? runs.value ?? [] : runs.value?.slice(0, 4) ?? []);
const sources = computed(() => catalogue.value?.sources.filter(source =>
  (state.value === 'all' || (state.value === 'stale' ? source.stale : source.status === state.value))
  && `${source.title} ${source.publisher} ${source.id}`.toLocaleLowerCase('it-IT').includes(query.value.trim().toLocaleLowerCase('it-IT'))) ?? []);
const ready = computed(() => catalogue.value?.sources.filter(source => source.status === 'ready').length ?? 0);
const retained = computed(() => catalogue.value?.sources.filter(source => source.stale).length ?? 0);
/** Translate known acquisition modes without treating local replay as a network check. */
function runMode(mode: string): string { return mode === 'offline-raw' ? 'Dati già raccolti' : mode === 'live' ? 'Raccolta dalle fonti' : 'Controllo dei dati'; }
useHead({ title: 'Aggiornamenti e qualità — IrpiniaConta' });
</script>

<template>
  <div class="supporting-page updates-page">
    <EditorialHeader eyebrow="La storia della raccolta" title="Dati curati," accent="nel tempo." description="Qui trovi i controlli registrati e lo stato delle fonti. La data del controllo non coincide necessariamente con l’anno a cui si riferiscono i dati." topic="updates"><NuxtLink to="/raccolta">Esplora le fonti <InterfaceIcon name="arrow-up-right" /></NuxtLink></EditorialHeader>
    <div class="editorial-figures"><div><strong>{{ runs?.length ?? '—' }}</strong><span>controlli registrati</span></div><div><strong>{{ catalogue ? ready : '—' }}</strong><span>fonti con dati disponibili</span></div><div><strong>{{ catalogue ? retained : '—' }}</strong><span>fonti per cui è stata conservata la versione precedente</span></div></div>
    <p class="supporting-notice"><strong>Gli aggiornamenti automatici sono in pausa.</strong> Se un aggiornamento non riesce, viene conservata l’ultima versione valida disponibile.</p>
    <section class="run-history" aria-labelledby="run-history-title">
      <header class="supporting-section-heading"><div><p class="eyebrow">I controlli nel tempo</p><h2 id="run-history-title">Da una verifica alla successiva.</h2></div><span>Più recenti per prime</span></header>
      <p v-if="runsError" class="notice" role="alert">Non riusciamo a mostrare i controlli registrati. Riprova più tardi.</p>
      <ol v-if="runs?.length" class="run-timeline"><li v-for="run in visibleRuns" :key="run.id"><span class="run-timeline-dot" aria-hidden="true" /><article class="run-card"><header><time :datetime="run.completed_at">{{ formatDate(run.completed_at) }}</time><span class="source-state">{{ runMode(run.mode) }}</span></header><dl class="run-figures"><div><dt>Fonti considerate</dt><dd>{{ run.attempted }}</dd></div><div><dt>Non disponibili o non riuscite</dt><dd>{{ run.failed }}</dd></div><div><dt>Fonti con dati disponibili al termine</dt><dd>{{ run.ready }}</dd></div></dl></article></li></ol>
      <p v-else-if="runs && !runsError" class="empty-state">Non ci sono controlli registrati da mostrare.</p>
      <button v-if="runs && runs.length > 4" class="supporting-button" :aria-expanded="showAll" @click="showAll = !showAll">{{ showAll ? 'Mostra le ultime quattro' : `Mostra tutti i ${runs.length} controlli` }}</button>
      <p class="supporting-note">Il numero delle fonti con dati disponibili si riferisce alla situazione al termine di ciascun controllo. Tra quelle non disponibili rientrano anche fonti ancora da verificare, non soltanto pagine non raggiungibili.</p>
    </section>
    <section class="source-checks" aria-labelledby="source-checks-title"><header class="supporting-section-heading"><div><p class="eyebrow">Il dettaglio delle verifiche</p><h2 id="source-checks-title">Ogni fonte, il suo stato.</h2></div></header>
      <p v-if="catalogueError" class="notice" role="alert">Lo stato delle fonti non è disponibile.</p>
      <template v-if="catalogue"><form class="source-filters source-filters--two" role="search" aria-label="Filtra lo stato delle fonti" @submit.prevent><label>Stato dei dati<select v-model="state"><option value="all">Tutti gli stati</option><option v-for="(label,id) in sourceStatusLabels" :key="id" :value="id">{{ label }}</option><option value="stale">Ultima versione valida conservata</option></select></label><label>Cerca una fonte<input v-model="query" type="search" placeholder="Titolo, ente o codice…"></label></form><p class="filter-result" role="status">{{ sources.length }} fonti</p><SourceList :sources="sources" /><p v-if="!sources.length" class="empty-state">Nessuna fonte corrisponde ai filtri.</p></template>
    </section>
  </div>
</template>
