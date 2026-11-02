<script setup lang="ts">
defineProps<{ name: 'arrow-up-right' | 'arrow-down' | 'arrow-up' | 'close' | 'plus' }>();
</script>

<template>
  <svg class="interface-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">
    <path v-if="name === 'arrow-up-right'" d="M5 19 19 5M8 5h11v11" />
    <path v-else-if="name === 'arrow-down'" d="M12 4v16m-6-6 6 6 6-6" />
    <path v-else-if="name === 'arrow-up'" d="M12 20V4m-6 6 6-6 6 6" />
    <path v-else-if="name === 'close'" d="M6 6l12 12M18 6 6 18" />
    <path v-else d="M12 5v14M5 12h14" />
  </svg>
</template>

<style scoped>
.interface-icon { display: inline-block; width: 1em; height: 1em; flex: none; vertical-align: -0.1em; }
</style>
