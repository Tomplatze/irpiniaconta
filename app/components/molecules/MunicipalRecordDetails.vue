<script setup lang="ts">
import LoadingStatus from '../atoms/LoadingStatus.vue';
import { formatPeriod } from '../../utils/presentation';
interface RecordItem { id:string; title:string; period:string; publisher:string; sourceTitle:string; sourceUrl:string; fields:Array<{label:string;value:string}> }
const props = defineProps<{code:string;group:string;recordId:string}>();
const {data:record,error,status} = useFetch<RecordItem>('/api/municipal-records', {
  query:computed(()=>({code:props.code,group:props.group,id:props.recordId})),
  key:`municipal-record-${props.code}-${props.group}-${props.recordId}`,
});
/** Source periods may describe acquisition, not the establishment of an institution. */
function periodLabel(period:string):string { return period.startsWith('undated') ? 'Rilevazione non datata dalla fonte' : `Periodo della fonte: ${formatPeriod(period)}`; }
/** Only allow links with a safe web protocol from published source metadata. */
function safeLink(value:string):string | null { try { const url = new URL(value); return ['http:','https:'].includes(url.protocol) ? url.href : null; } catch { return null; } }
</script>
<template>
  <div class="municipal-record__details" :aria-busy="status==='pending'">
    <p v-if="error" role="alert">Non è stato possibile caricare il dettaglio. Chiudi e riapri la voce per riprovare.</p>
    <LoadingStatus v-else-if="status==='pending' && !record" label="Caricamento del dettaglio…" />
    <template v-else-if="record">
      <p class="municipal-record__period">{{ periodLabel(record.period) }}</p>
      <dl v-if="record.fields.length" class="municipal-record__fields"><div v-for="(field,index) in record.fields" :key="`${field.label}-${index}`"><dt>{{ field.label }}</dt><dd><a v-if="safeLink(field.value)" :href="safeLink(field.value)!" target="_blank" rel="noreferrer">{{ field.value }} ↗</a><template v-else>{{ field.value }}</template></dd></div></dl>
      <a v-if="safeLink(record.sourceUrl)" class="municipal-record__source" :href="safeLink(record.sourceUrl)!" target="_blank" rel="noreferrer">{{ record.publisher }} · {{ record.sourceTitle }} ↗</a><span v-else class="municipal-record__source">{{ record.publisher }} · {{ record.sourceTitle }}</span>
    </template>
  </div>
</template>
