<script setup lang="ts">
import TerritoryPage from '../../components/organisms/TerritoryPage.vue';
const route = useRoute();
const category = computed(() => String(route.params.id));
const code = computed(() => typeof route.query.code === 'string' ? route.query.code : undefined);
if (route.query.code !== undefined && (!code.value || !/^064\d{3}$/.test(code.value))) {
  throw createError({statusCode:404,statusMessage:'Comune non trovato'});
}
</script>
<template><div class="territory-route"><TerritoryPage :key="`${category}:${code ?? 'province'}`" :category="category" :code="code" /></div></template>
