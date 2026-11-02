<script setup lang="ts">
import TopicIllustration from '../atoms/TopicIllustration.vue';
defineProps<{ eyebrow: string; title: string; accent?: string; description: string; topic: string }>();
</script>

<template>
  <header class="editorial-header">
    <div class="editorial-introduction">
      <p class="eyebrow">{{ eyebrow }}</p>
      <h1>{{ title }}<span v-if="accent">{{ ' ' + accent }}</span></h1>
      <p class="editorial-lead">{{ description }}</p>
      <div v-if="$slots.default" class="hero-actions"><slot /></div>
    </div>
    <div class="editorial-art"><slot name="visual"><TopicIllustration :topic="topic" /></slot></div>
  </header>
</template>
