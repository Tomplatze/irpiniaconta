<script setup lang="ts">
defineProps<{ label: string }>();
</script>

<template>
  <p class="loading-status" role="status"><span class="loading-status__spinner" aria-hidden="true" />{{ label }}</p>
</template>

<style scoped>
.loading-status { display: flex; align-items: center; gap: 10px; margin: 18px 0; color: #245644; font-size: .9rem; font-weight: 600; }
.loading-status__spinner { width: 18px; height: 18px; flex: 0 0 18px; border: 2px solid #b8cdc0; border-top-color: #16533f; border-radius: 50%; animation: loading-spin .8s linear infinite; }
@keyframes loading-spin { to { transform: rotate(360deg); } }
@media (prefers-reduced-motion: reduce) { .loading-status__spinner { animation: none; } }
</style>
