<script setup lang="ts">
import LoadingStatus from '../atoms/LoadingStatus.vue';
import MunicipalRecordDetails from './MunicipalRecordDetails.vue';
interface RecordIndexItem { id:string; title:string; reference?:string }
interface RecordIndex { total:number; records:RecordIndexItem[] }
const props = defineProps<{code:string;group:string}>();
const search = ref('');
const pageSize = 10;
const visibleCount = ref(pageSize);
const openRecords = reactive(new Set<string>());
const {data:index,error,status} = useFetch<RecordIndex>('/api/municipal-records', {
  query:computed(()=>({code:props.code,group:props.group,view:'index'})),
  key:`municipal-record-index-${props.code}-${props.group}`,
});
const filtered = computed(() => {
  const term = search.value.trim().toLocaleLowerCase('it');
  return (index.value?.records ?? []).filter(record=>`${record.title} ${record.reference ?? ''}`.toLocaleLowerCase('it').includes(term));
});
const visibleRecords = computed(() => filtered.value.slice(0,visibleCount.value));
const remaining = computed(() => filtered.value.length-visibleRecords.value.length);
/** Reveal the next batch without changing already open disclosures. */
function loadMore():void { visibleCount.value += pageSize; }
/** Keep details dormant until their own native disclosure is opened. */
function toggleRecord(id:string,event:Event):void {
  if ((event.target as HTMLDetailsElement).open) openRecords.add(id);
  else openRecords.delete(id);
}
watch(search, () => { visibleCount.value=pageSize; });
watch(() => [props.code,props.group], () => { search.value=''; visibleCount.value=pageSize; openRecords.clear(); });
</script>
<template>
  <div class="municipal-records__content" :aria-busy="status==='pending'">
    <p class="municipal-records__note">Gli elenchi si basano sulle fonti indicate e potrebbero non essere completi. Mostriamo indirizzi e recapiti quando sono disponibili.</p>
    <p v-if="error" role="alert">Non è stato possibile caricare l’elenco. Chiudi e riapri la sezione per riprovare.</p>
    <LoadingStatus v-else-if="status==='pending' && !index" label="Caricamento dell’elenco…" />
    <template v-else-if="index">
      <p v-if="index.total===0" class="municipal-records__empty">Nessun dettaglio disponibile nella raccolta per questo comune.</p>
      <template v-else>
        <label v-if="index.total>pageSize" class="municipal-records__search">Cerca nell’elenco<input v-model="search" type="search" placeholder="Cerca per titolo o codice" /></label>
        <p class="municipal-records__count" aria-live="polite">{{ visibleRecords.length.toLocaleString('it-IT') }} di {{ filtered.length.toLocaleString('it-IT') }} {{ filtered.length===1 ? 'voce' : 'voci' }}<template v-if="search.trim()"> · {{ index.total.toLocaleString('it-IT') }} nell’elenco completo</template></p>
        <p v-if="filtered.length===0" class="municipal-records__empty">Nessuna voce corrisponde alla ricerca.</p>
        <div class="municipal-records__list">
          <details v-for="item in visibleRecords" :key="item.id" class="municipal-record" :open="openRecords.has(item.id)" @toggle="toggleRecord(item.id,$event)">
            <summary><span>{{ item.title }}<small v-if="item.reference">{{ item.reference }}</small></span><span class="municipal-record__icon" aria-hidden="true" /></summary>
            <MunicipalRecordDetails v-if="openRecords.has(item.id)" :code="code" :group="group" :record-id="item.id" />
          </details>
        </div>
        <button v-if="remaining>0" type="button" class="municipal-records__more" @click="loadMore">Carica altre {{ Math.min(pageSize,remaining) }} {{ remaining===1 ? 'voce' : 'voci' }}</button>
      </template>
    </template>
  </div>
</template>
