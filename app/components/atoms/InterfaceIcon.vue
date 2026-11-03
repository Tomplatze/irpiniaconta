<script setup lang="ts">
defineProps<{ name: 'arrow-up-right' | 'arrow-down' | 'arrow-up' | 'close' | 'plus' | 'heart-pulse' }>();
</script>

<template>
  <svg class="interface-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">
    <path v-if="name === 'arrow-up-right'" d="M5 19 19 5M8 5h11v11" />
    <path v-else-if="name === 'arrow-down'" d="M12 4v16m-6-6 6 6 6-6" />
    <path v-else-if="name === 'arrow-up'" d="M12 20V4m-6 6 6-6 6 6" />
    <path v-else-if="name === 'close'" d="M6 6l12 12M18 6 6 18" />
    <!-- Heart icon: Heroicons by Tailwind Labs, MIT; see third-party/heroicons-LICENSE.txt. -->
    <path v-else-if="name === 'heart-pulse'" fill="currentColor" stroke="none" d="m11.645 20.91-.007-.003-.022-.012a15 15 0 0 1-.383-.218 25.2 25.2 0 0 1-4.244-3.17C4.688 15.36 2.25 12.174 2.25 8.25 2.25 5.322 4.714 3 7.688 3A5.5 5.5 0 0 1 12 5.052 5.5 5.5 0 0 1 16.313 3c2.973 0 5.437 2.322 5.437 5.25 0 3.925-2.438 7.111-4.739 9.256a25 25 0 0 1-4.244 3.17 15 15 0 0 1-.383.219l-.022.012-.007.004-.003.001a.75.75 0 0 1-.704 0l-.003-.001Z" />
    <path v-else d="M12 5v14M5 12h14" />
  </svg>
</template>

<style scoped>
.interface-icon { display: inline-block; width: 1em; height: 1em; flex: none; vertical-align: -0.1em; }
</style>
