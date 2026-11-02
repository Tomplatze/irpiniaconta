<script setup lang="ts">
const props = defineProps<{ topic: string; metric?: string }>();

// Resolve only artwork that exists; unknown metrics must not inherit a misleading picture.
const illustrations = import.meta.glob<string>('../../assets/illustrations/*.webp', {
  eager: true,
  query: '?url',
  import: 'default',
});

const imageSource = computed(() => illustrations[
  `../../assets/illustrations/${props.metric ?? `topic-${props.topic}`}.webp`
] ?? null);
</script>

<template>
  <img
    v-if="imageSource"
    :src="imageSource"
    class="topic-illustration topic-illustration--image"
    alt=""
    aria-hidden="true"
    decoding="async"
    loading="lazy"
  />
</template>
