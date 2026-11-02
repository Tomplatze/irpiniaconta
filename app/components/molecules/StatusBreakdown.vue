<script setup lang="ts">
const props = defineProps<{ label: string; items: Array<{ id: string; label: string; count: number }> }>();
const total = computed(() => props.items.reduce((sum, item) => sum + item.count, 0));
</script>

<template>
  <figure class="status-breakdown" :aria-label="label">
    <div class="status-breakdown-track" aria-hidden="true"><span v-for="item in items" :key="item.id" :class="`source-tone-${item.id}`" :style="{ width: `${total ? item.count / total * 100 : 0}%` }" /></div>
    <figcaption><span v-for="item in items" :key="item.id"><i :class="`source-tone-${item.id}`" aria-hidden="true" /><strong>{{ item.count }}</strong> {{ item.label }}</span></figcaption>
  </figure>
</template>
