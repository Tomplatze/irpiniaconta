<script setup lang="ts">
import TerritoryPage from '../../components/organisms/TerritoryPage.vue';
const route = useRoute();
const code = computed(()=>String(route.params.code));
if(!/^064\d{3}$/.test(code.value)) throw createError({statusCode:404,statusMessage:'Comune non trovato'});
</script>
<template><div class="territory-route"><TerritoryPage :key="code" :code="code" /></div></template>
