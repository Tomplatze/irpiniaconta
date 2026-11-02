<script setup lang="ts">
import type { MunicipalCrest } from '../../../shared/municipalCrests';

const props = defineProps<{ crest?: MunicipalCrest; name: string; decorative?: boolean; large?: boolean }>();
const failed = ref(false);
watch(() => props.crest?.file, () => { failed.value = false; });
</script>

<template>
  <figure v-if="crest?.file && !failed" class="municipal-crest" :class="{ 'municipal-crest--detailed': large }">
    <img :src="crest.file" :alt="decorative ? '' : `Stemma del Comune di ${name}`" loading="lazy" decoding="async" @error="failed = true" />
  </figure>
</template>
