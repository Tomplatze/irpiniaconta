<script setup lang="ts">
import MunicipalRecordPage from './MunicipalRecordPage.vue';
const props = defineProps<{code:string;group:string;label:string}>();
const expanded = ref(false);
watch(() => [props.code,props.group], () => { expanded.value=false; });
</script>
<template>
  <details class="municipal-records" :open="expanded" @toggle="expanded=($event.target as HTMLDetailsElement).open">
    <summary>{{ label }}</summary>
    <MunicipalRecordPage v-if="expanded" :code="code" :group="group" />
  </details>
</template>
