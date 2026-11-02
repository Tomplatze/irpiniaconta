<script setup lang="ts">
import InterfaceIcon from '~/components/atoms/InterfaceIcon.vue';
import type { SourceEntry } from '../../../shared/catalogue';
import { formatDate, formatPeriod } from '../../utils/presentation';
import { sourceStatusLabels, sourceReachability, sourceGeography, collectionLimitation, licenseDescription } from '../../utils/sourcePresentation';
defineProps<{ sources: SourceEntry[] }>();
/** Only web addresses can become links. */
function safeLink(value: string): string | null { try { const url = new URL(value); return ['http:','https:'].includes(url.protocol) ? url.href : null; } catch { return null; } }
const sourceNotes: Record<string,string> = {
  'DEM-01': 'La popolazione al 1° gennaio 2026 è una stima. I dati sui cambiamenti della popolazione sono presentati separatamente.',
  'DEM-02': 'I dati 2025 sono provvisori; quelli dal 2021 al 2024 tengono conto del censimento. Le popolazioni al 31 dicembre restano distinte dalle stime al 1° gennaio.',
};
</script>

<template>
  <div class="source-card-grid" aria-label="Voci del catalogo">
    <article v-for="source in sources" :key="source.id" class="integration-card">
      <header class="source-card-top"><span class="source-state" :class="`source-state--${source.status}`">{{ sourceStatusLabels[source.status] }}</span></header>
      <p class="source-publisher">{{ source.publisher }}</p><h3>{{ source.title }}</h3>
      <p class="source-geography">{{ sourceGeography(source.geography) }}</p>
      <div v-if="source.status === 'ready'" class="source-key-facts"><span><strong>{{ source.dataset?.indicators.length ?? 0 }}</strong> indicatori</span><span v-if="source.entity_count"><strong>{{ source.entity_count.toLocaleString('it-IT') }}</strong> voci nella raccolta</span></div>
      <p v-else-if="source.blocker" class="source-limitation">{{ collectionLimitation(source.id) }}</p>
      <p v-if="source.stale" class="source-limitation">Ultima versione valida conservata dopo un aggiornamento non riuscito.</p>
      <p v-if="source.update_error" class="source-limitation">L’ultimo aggiornamento non è riuscito.</p>
      <div class="source-check"><span>{{ sourceReachability(source.landing_status) }}</span><span v-if="source.checked_at">Controllo registrato: {{ formatDate(source.checked_at) }}</span><span v-else>Data di controllo non disponibile</span></div>
      <a class="official-source-link" :href="source.landing_url" target="_blank" rel="noreferrer">{{ source.publisher }} · Fonte istituzionale <InterfaceIcon name="arrow-up-right" /></a>
      <details v-if="source.dataset" class="source-metadata"><summary>Periodi, copertura e riferimenti</summary>
        <p v-if="sourceNotes[source.id]">{{ sourceNotes[source.id] }}</p>
        <p v-if="source.dataset.license">Licenza dichiarata: {{ licenseDescription(source.dataset.license) }}</p>
        <p v-if="source.entity_count">{{ source.associated_entity_count.toLocaleString('it-IT') }} delle {{ source.entity_count.toLocaleString('it-IT') }} voci sono associate a un comune. L’elenco potrebbe non essere completo.</p>
        <div v-for="metric in source.dataset.indicators" :key="metric.id" class="source-coverage"><div><strong>{{ metric.label }}</strong><span>{{ metric.observed_count }}/118</span></div><span class="source-coverage-track" aria-hidden="true"><i :style="{ width: `${Math.max(0, Math.min(100, metric.observed_count / 118 * 100))}%` }" /></span><p>Comuni con dato disponibile nell’ultimo periodo, {{ formatPeriod(metric.latest_period) }} · {{ metric.periods.length }} {{ metric.periods.length===1 ? 'periodo disponibile' : 'periodi disponibili' }}. Mancanti {{ metric.missing_count }}, riservati {{ metric.suppressed_count }}, assenti {{ metric.absent_count }}.</p></div>
        <details v-if="source.dataset.artifacts.length"><summary>Consulta i dati originali</summary><ul class="source-artifacts"><li v-for="(artifact,index) in source.dataset.artifacts" :key="index"><a v-if="safeLink(artifact.url)" :href="safeLink(artifact.url)!" target="_blank" rel="noreferrer">Fonte originale {{ index+1 }} <InterfaceIcon name="arrow-up-right" /></a><span>{{ formatDate(artifact.retrieved_at) }}</span></li></ul></details>
      </details>
    </article>
  </div>
</template>
