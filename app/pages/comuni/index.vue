<script setup lang="ts">
import type { SectionMap, SectionResponse } from '../../../shared/sections';
import EditorialHeader from '../../components/molecules/EditorialHeader.vue';
import MunicipalMetricMap from '../../components/molecules/MunicipalMetricMap.vue';
import MunicipalCrest from '../../components/atoms/MunicipalCrest.vue';
import type { MunicipalCrestManifest } from '../../../shared/municipalCrests';
import { sectionPeriod } from '../../utils/sections';
const {data: publication, error} = await useFetch<SectionResponse>('/api/section', {query:{category:'demography',metric:'population'}});
const {data: map} = await useFetch<SectionMap>('/api/section-map');
const {data: crests} = await useFetch<MunicipalCrestManifest>('/api/municipal-crests', {key: 'municipal-crests'});
const crestsByCode = computed(() => new Map(crests.value?.records.map(crest => [crest.code, crest]) ?? []));
const search = ref('');
const headerSearchFocused = ref(false);
/** Close suggestions only when focus leaves the search controls. */
function onHeaderSearchBlur(event: FocusEvent): void {
  if (!(event.currentTarget as HTMLElement).contains(event.relatedTarget as Node | null)) headerSearchFocused.value = false;
}
/** Keep accents and official names in the registry, normalizing only the search text. */
function searchable(value: string): string {
  return value.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('it-IT').trim();
}
const municipalities = computed(() => publication.value?.municipalities.filter(town => searchable(`${town.name} ${town.code}`).includes(searchable(search.value))).toSorted((left,right) => left.name.localeCompare(right.name,'it-IT')) ?? []);
const groups = computed(() => {
  const result = new Map<string, typeof municipalities.value>();
  for (const town of municipalities.value) {
    const initial = town.name.charAt(0).toLocaleUpperCase('it-IT');
    const group = result.get(initial) ?? [];
    group.push(town);
    result.set(initial,group);
  }
  return [...result].map(([initial,towns]) => ({initial,towns}));
});
useHead({title:'I comuni — IrpiniaConta'});
</script>
<template>
  <div class="municipality-index">
    <ClientOnly>
      <Teleport to="#topic-navigation-slot">
        <div class="header-town-search" @focusin="headerSearchFocused = true" @focusout="onHeaderSearchBlur" @keydown.esc="headerSearchFocused = false">
          <label class="sr-only" for="header-town-search">Cerca un comune</label>
          <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5" /><path d="m15.5 15.5 4.5 4.5" /></svg>
          <input id="header-town-search" v-model="search" type="search" placeholder="Cerca comune" autocomplete="off" aria-controls="header-town-results" />
          <div v-if="headerSearchFocused && search.trim()" id="header-town-results" class="header-town-results">
            <p v-if="!municipalities.length" role="status">Nessun comune trovato.</p>
            <template v-else>
              <NuxtLink v-for="town in municipalities.slice(0, 6)" :key="town.code" :to="`/comuni/${town.code}`">{{ town.name }} <span aria-hidden="true">↗</span></NuxtLink>
              <a v-if="municipalities.length > 6" href="#elenco-comuni" @click="headerSearchFocused = false">Mostra tutti i {{ municipalities.length }} risultati ↓</a>
            </template>
          </div>
        </div>
      </Teleport>
    </ClientOnly>
    <EditorialHeader eyebrow="Un territorio, tante storie" title="118 comuni." accent="Ognuno conta." description="Scegli un comune per aprire il suo ritratto: residenti, economia, servizi e paesaggio. La mappa conserva il contesto dell’Irpinia, ogni pagina mette al centro il suo territorio." topic="municipalities">
      <a class="action-primary" href="#elenco-comuni">Trova il tuo comune ↓</a><NuxtLink to="/confronta">Confronta due comuni ↗</NuxtLink>
      <template #visual>
        <section v-if="map && publication" class="territory-map municipality-index-map" aria-label="Scegli un comune sulla mappa">
          <p class="eyebrow">La popolazione dei comuni</p>
          <MunicipalMetricMap :map="map" :values="publication.distribution" :unit="publication.metric.unit" selected-code="" :period="sectionPeriod(publication.metric.latest_period,publication.metric.id)" navigation />
          <p class="map-period-label">{{ sectionPeriod(publication.metric.latest_period,publication.metric.id) }} · ISTAT</p>
        </section>
      </template>
    </EditorialHeader>
    <p v-if="error" class="notice" role="alert">Non riusciamo a mostrare l’elenco dei comuni. Riprova più tardi.</p>
    <section id="elenco-comuni" class="municipality-directory" aria-labelledby="directory-title">
      <header class="directory-toolbar"><div><p class="eyebrow">Le pagine dei comuni</p><h2 id="directory-title">Da Aiello a Zungoli.</h2></div><label>Cerca il tuo comune<input v-model="search" type="search" placeholder="Nome o codice ISTAT" aria-controls="municipality-results"></label></header>
      <p class="directory-count" role="status">{{ municipalities.length }} {{ municipalities.length===1 ? 'comune trovato' : 'comuni trovati' }}</p>
      <div id="municipality-results">
        <p v-if="!municipalities.length && !error" class="empty-state">Nessun comune corrisponde alla ricerca. Prova con un altro nome o codice.</p>
        <section v-for="group in groups" :key="group.initial" class="municipality-letter" :aria-label="`Comuni con iniziale ${group.initial}`">
          <h3 aria-hidden="true">{{ group.initial }}</h3>
          <ul><li v-for="town in group.towns" :key="town.code"><NuxtLink :to="`/comuni/${town.code}`"><MunicipalCrest :crest="crestsByCode.get(town.code)" :name="town.name" decorative /><span class="municipality-directory-name"><strong>{{ town.name }}</strong><small>ISTAT {{ town.code }}</small></span><span aria-hidden="true">↗</span></NuxtLink></li></ul>
        </section>
      </div>
    </section>
  </div>
</template>
