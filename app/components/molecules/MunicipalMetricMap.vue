<script setup lang="ts">
import type { SectionMap, SectionMeasurement, SectionOverview } from '../../../shared/sections';
import type { MunicipalCrest as CrestRecord } from '../../../shared/municipalCrests';
import MunicipalCrest from '../atoms/MunicipalCrest.vue';
import { formatValue, unitLabel, statusLabel } from '../../utils/presentation';
const props = withDefaults(defineProps<{
  map: SectionMap;
  values?: SectionMeasurement[];
  unit?: string;
  selectedCode?: string;
  period?: string;
  navigation?: boolean;
  directory?: { municipalities: SectionOverview['municipalities']; crests: ReadonlyMap<string, CrestRecord> };
}>(), { values: () => [], unit: '', selectedCode: '' });
const emit = defineEmits<{ select: [code: string] }>();
/** Preserve the selection behavior on embedded dashboards and native links elsewhere. */
function choose(event: MouseEvent, code: string): void {
  if (!props.navigation) { event.preventDefault(); emit('select',code); }
}
function chooseWithSpace(event: KeyboardEvent, code: string): void {
  if (!props.navigation) { event.preventDefault(); emit('select',code); }
}
const hoverCode = ref('');
const focusCode = ref('');
const activeCode = computed(() => hoverCode.value || focusCode.value);
const directoryNames = computed(() => new Map(props.directory?.municipalities.map(town => [town.code, town.name])));
const activeDirectoryName = computed(() => directoryNames.value.get(activeCode.value));
const activeDirectoryCrest = computed(() => props.directory?.crests.get(activeCode.value));

/** Keep the focused municipality available when the pointer leaves the map. */
function focusTown(code: string): void {
  hoverCode.value = '';
  focusCode.value = code;
}
const filterId = `map-lift-${useId().replaceAll(':','')}`;
const records = computed(() => new Map(props.values.map(row=>[row.code,row])));
const measured = computed(() => props.values.filter(row=>row.status==='observed' && row.value!==null).map(row=>row.value!));
const minimum = computed(() => measured.value.length ? Math.min(...measured.value) : 0);
const maximum = computed(() => measured.value.length ? Math.max(...measured.value) : 0);
const selected = computed(() => records.value.get(props.selectedCode || activeCode.value));
const hoverReadout = computed(() => props.selectedCode && activeCode.value!==props.selectedCode ? records.value.get(activeCode.value) : undefined);
const selectedFeature = computed(() => props.map.features.find(feature=>feature.code===props.selectedCode));
const selectedTown = computed(() => records.value.get(props.selectedCode));
const palette = ['#dce9d5','#abc6a0','#75a07b','#43775d','#174b3b'];
/** Five equal-width value classes; missing source values remain neutral. */
function fill(code: string): string {
  const record = records.value.get(code);
  if (record?.status!=='observed' || record.value===null) return '#dfded5';
  const fraction = maximum.value===minimum.value ? .5 : (record.value-minimum.value)/(maximum.value-minimum.value);
  return palette[Math.min(4,Math.floor(fraction*5))]!;
}
function accessibleLabel(code: string): string {
  if (props.directory) return `${directoryNames.value.get(code) ?? code}. Apri il comune.`;
  const row = records.value.get(code);
  return row ? `${row.name}: ${formatValue(row.value,props.unit)} ${unitLabel(props.unit)}, ${statusLabel(row.status)}. ${props.period ?? ''}. Apri il comune.` : code;
}
</script>
<template>
  <figure class="municipal-metric-map" :class="{ 'municipal-metric-map--focused': selectedFeature, 'municipal-metric-map--directory': directory }">
    <div class="map-toolbar"><span class="eyebrow">{{ selectedTown ? 'Il comune nel territorio' : '118 territori, una provincia' }}</span></div>
    <div class="map-stage">
      <svg :viewBox="map.view_box" role="group" :aria-label="directory ? 'Mappa dei 118 comuni della provincia di Avellino' : 'Mappa dei 118 comuni: i colori indicano i valori dell’indicatore.'" @mouseleave="hoverCode=''" @focusout="focusCode=''">
        <defs v-if="selectedFeature"><filter :id="filterId" x="-30%" y="-30%" width="160%" height="180%"><feDropShadow dx="0" dy="5" stdDeviation="3" flood-color="#12392d" flood-opacity=".4" /></filter></defs>
        <g transform="translate(0,7)" aria-hidden="true" class="map-base"><path v-for="feature in map.features" :key="feature.code" :d="feature.path" fill-rule="evenodd" /></g>
        <a v-for="feature in map.features" :key="feature.code" :href="navigation ? `/comuni/${feature.code}` : undefined" tabindex="0" :role="navigation ? undefined : 'button'" :aria-label="accessibleLabel(feature.code)" :aria-current="feature.code===selectedCode && navigation ? 'page' : undefined" @mouseenter="hoverCode=feature.code" @focus="focusTown(feature.code)" @click="choose($event,feature.code)" @keydown.space="chooseWithSpace($event,feature.code)" @keydown.enter="!navigation && $emit('select',feature.code)">
          <path :d="feature.path" :fill="directory ? undefined : fill(feature.code)" fill-rule="evenodd" class="municipal-area" :class="{ 'municipal-area--selected': feature.code === selectedCode, 'municipal-area--active': feature.code === activeCode && feature.code !== selectedCode }" />
        </a>
        <g v-if="selectedFeature" transform="translate(0,-8)" class="map-permanent-selection" aria-hidden="true" :filter="`url(#${filterId})`">
          <path :d="selectedFeature.path" :fill="fill(selectedFeature.code)" fill-rule="evenodd" class="map-selection-halo" />
          <path :d="selectedFeature.path" :fill="fill(selectedFeature.code)" fill-rule="evenodd" class="map-selection-outline" />
        </g>
      </svg>
    </div>
    <div class="map-readouts">
      <div class="map-readout-primary" aria-live="polite" aria-atomic="true">
        <template v-if="directory && activeDirectoryName">
          <div class="map-readout-identity"><small>Comune esplorato</small><strong>{{ activeDirectoryName }}</strong></div>
          <MunicipalCrest :crest="activeDirectoryCrest" :name="activeDirectoryName" />
        </template>
        <template v-else-if="selected"><div class="map-readout-identity"><small>{{ selectedCode ? 'Comune selezionato' : 'Comune esplorato' }}</small><strong>{{ selected.name }}</strong><small v-if="period">{{ period }}</small></div><span class="map-readout-value">{{ selected.status==='observed' ? formatValue(selected.value,unit)+' '+unitLabel(unit) : statusLabel(selected.status) }}</span></template>
        <template v-else><div class="map-readout-identity"><strong>Esplora l’Irpinia</strong><small>{{ directory ? 'Seleziona un comune per aprire la sua scheda.' : 'Tocca un comune per aprire la sua pagina.' }}</small></div></template>
      </div>
      <div v-if="selectedTown" class="map-readout-exploration" aria-live="polite" aria-atomic="true"><template v-if="hoverReadout"><strong>{{ hoverReadout.name }}</strong><span>{{ hoverReadout.status==='observed' ? formatValue(hoverReadout.value,unit)+' '+unitLabel(unit) : statusLabel(hoverReadout.status) }}</span></template><span v-else class="map-readout-hint">Esplora gli altri comuni sulla mappa.</span></div>
    </div>
    <figcaption v-if="directory" class="visual-note">Confini comunali ISTAT 2026, semplificati.</figcaption>
    <figcaption v-else class="map-key"><span v-if="measured.length">{{ formatValue(minimum,unit) }} <span class="map-scale" aria-hidden="true"><i v-for="color in palette" :key="color" :style="{background:color}" /></span> {{ formatValue(maximum,unit) }} {{ unitLabel(unit) }}</span><span><i class="map-no-data" /> Senza dato</span></figcaption>
    <p v-if="!directory" class="visual-note">I colori dividono i valori disponibili in cinque fasce uguali, dal più basso al più alto. I confini comunali ISTAT 2026 sono semplificati.<template v-if="selectedTown"> Il bordo color terracotta evidenzia {{ selectedTown.name }} anche mentre esplori gli altri comuni.</template></p>
  </figure>
</template>
