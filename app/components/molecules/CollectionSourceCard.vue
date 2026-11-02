<script setup lang="ts">
import InterfaceIcon from '~/components/atoms/InterfaceIcon.vue';
import type { CollectionScope, CollectedDataset } from '../../../shared/collection';
import { collectionStatusLabels, collectionPeriods, collectionSummary, collectionLimitation, licenseDescription } from '../../utils/sourcePresentation';
const props = defineProps<{ source: CollectionScope; datasets: CollectedDataset[] }>();
const related = computed(() => props.datasets.filter(dataset => props.source.dataset_ids.includes(dataset.id)));
/** Only web addresses can become links. */
function safeLink(value: string): string | null { try { const url = new URL(value); return ['http:','https:'].includes(url.protocol) ? url.href : null; } catch { return null; } }
</script>

<template>
  <article class="collection-source source-collection-card">
    <header class="source-card-top"><span class="source-state" :class="`source-state--${source.status}`">{{ collectionStatusLabels[source.status] }}</span></header>
    <p class="source-publisher">{{ source.publisher }}</p><h3>{{ source.title }}</h3>
    <p class="source-summary">{{ collectionSummary(source.id,source.ui_summary) }}</p>
    <p v-if="source.id==='DEM-04' && source.status==='integrated'" class="source-summary">La stima delle persone residenti con cittadinanza straniera al 1° gennaio 2026 è disponibile nella sezione Demografia. I dati del 2024 restano distinti.</p>
    <div class="collection-coverage"><div><strong>{{ source.coverage }}<small>/118</small></strong><span>comuni con almeno una voce<br>nella raccolta disponibile</span></div><span class="source-coverage-track" aria-hidden="true"><i :style="{ width: `${Math.max(0, Math.min(100, source.coverage / 118 * 100))}%` }" /></span></div>
    <p class="source-periods">{{ collectionPeriods(source.periods) }}</p>
    <p v-if="source.blocker" class="source-limitation">{{ collectionLimitation(source.id) }}</p>
    <details v-if="source.available_product_fields.length" class="source-metadata"><summary>Dati presenti nella raccolta</summary><ul><li v-for="field in source.available_product_fields" :key="field">{{ source.id==='ECO-03' ? field.replace(' - Frequenza',' · numero di dichiarazioni').replace(' - Ammontare in euro',' · importo in euro') : field }}</li></ul></details>
    <details v-for="dataset in related" :key="dataset.id" class="source-metadata">
      <summary>{{ dataset.title }}<span class="source-detail-count">{{ dataset.record_count.toLocaleString('it-IT') }} voci · {{ dataset.coverage }}/118 comuni</span></summary>
      <p><strong>{{ dataset.publisher }}</strong> · {{ dataset.format }}</p><p>{{ dataset.period_semantics.replace('dei record', 'delle singole voci') }}: {{ collectionPeriods(dataset.periods) }}</p>
      <p>Queste sono le informazioni raccolte dalla fonte; gli indicatori mostrati nell’atlante sono controllati separatamente.</p>
      <p v-if="dataset.license">Licenza dichiarata: {{ licenseDescription(dataset.license) }}</p>
      <details><summary>Copertura per anno o periodo</summary><ul><li v-for="(count, period) in dataset.coverage_by_period" :key="period">{{ collectionPeriods([String(period)]) }}: {{ count }}/118 comuni</li></ul></details>
      <details><summary>Consulta i dati originali</summary><p v-for="(url,index) in dataset.source_urls" :key="url"><a v-if="safeLink(url)" :href="safeLink(url)!" target="_blank" rel="noopener noreferrer">Fonte originale {{ index+1 }} <InterfaceIcon name="arrow-up-right" /></a><span v-else>Indirizzo della fonte non disponibile</span></p></details>
    </details>
    <a class="official-source-link" :href="source.landing_url" target="_blank" rel="noopener noreferrer">{{ source.publisher }} · Fonte del catalogo <InterfaceIcon name="arrow-up-right" /></a>
  </article>
</template>
