<script setup lang="ts">
import type { SectionDefinition } from '../../../shared/sections';
import TopicIllustration from '../atoms/TopicIllustration.vue';
const props = defineProps<{ categories: Pick<SectionDefinition, 'id' | 'label'>[]; order: string[]; destinations?: Record<string, string>; currentId?: string }>();
const panel = ref<HTMLElement | null>(null);
const open = ref(false);
const active = ref('');
const panelId = `topic-menu-${useId().replaceAll(':', '')}`;
const current = computed(() => props.categories.find(category => category.id === (active.value || props.currentId)));
let observer: IntersectionObserver | undefined;

/** Track the chapter crossing the reading line, including chapters taller than the viewport. */
function observeChapters(): void {
  observer?.disconnect();
  active.value = '';
  observer = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (entry.isIntersecting) active.value = entry.target.id.replace('tema-', '');
      else if (entry.target.id === `tema-${active.value}`) active.value = '';
    }
  }, { rootMargin: `-${Math.round(window.innerHeight*.22)}px 0px -${Math.floor(window.innerHeight*.77)}px 0px`, threshold: 0 });
  for (const category of props.categories) {
    const chapter = document.getElementById(`tema-${category.id}`);
    if (chapter) observer.observe(chapter);
  }
}
onMounted(() => {
  observeChapters();
  window.addEventListener('resize', observeChapters, { passive: true });
});
watch(() => props.categories, async () => { await nextTick(); observeChapters(); });
onBeforeUnmount(() => {
  observer?.disconnect();
  window.removeEventListener('resize', observeChapters);
});

/** Native popovers handle Escape, outside clicks and focus return. */
function closeMenu(): void { panel.value?.hidePopover(); }
function onToggle(event: Event): void { open.value = (event as ToggleEvent).newState === 'open'; }
/** Retain native modified-click behavior while routing dedicated topic pages locally. */
function followTopic(event: MouseEvent, id: string): void {
  closeMenu();
  const destination = props.destinations?.[id];
  if (!destination || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  event.preventDefault();
  void navigateTo(destination);
}
</script>
<template>
  <aside class="topic-navigator" aria-label="Navigazione dei temi">
    <button class="topic-trigger" :popovertarget="panelId" :aria-expanded="open" :aria-controls="panelId" :aria-label="current ? `Menu dei temi. Stai leggendo: ${current.label}` : 'Scegli un tema. Apri menu dei temi'">
      <span class="topic-trigger-label"><small>{{ current ? 'Stai leggendo' : 'Esplora l’atlante' }}</small><strong>{{ current?.label ?? 'Scegli un tema' }}</strong></span>
      <span class="topic-trigger-short" aria-hidden="true">Temi <span v-if="current">{{ String(order.indexOf(current.id)+1).padStart(2,'0') }}</span></span>
      <svg class="topic-trigger-symbol" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6H20M4 12H16M4 18H20" /></svg>
    </button>
    <nav :id="panelId" ref="panel" popover="auto" class="topic-popover" aria-label="Vai a un tema" @toggle="onToggle">
      <header><p class="eyebrow">I temi dell’atlante</p><h2>Scegli un tema</h2><button aria-label="Chiudi menu dei temi" @click="closeMenu">×</button></header>
      <a v-for="category in categories" :key="category.id" :href="destinations?.[category.id] ?? `#tema-${category.id}`" :aria-current="current?.id===category.id ? 'location' : undefined" @click="followTopic($event,category.id)">
        <span class="topic-menu-number">{{ String(order.indexOf(category.id)+1).padStart(2,'0') }}</span><TopicIllustration :topic="category.id" /><span>{{ category.label }}</span><span class="topic-menu-arrow" aria-hidden="true">↗</span>
      </a>
    </nav>
  </aside>
</template>
