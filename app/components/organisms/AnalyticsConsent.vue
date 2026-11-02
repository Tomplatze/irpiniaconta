<script setup lang="ts">
import InterfaceIcon from '~/components/atoms/InterfaceIcon.vue';
const { available, preview, visible, storageError, start, choose } = useAnalyticsConsent();

const syncChoice = (event: StorageEvent) => {
  if (event.key === 'irpiniaconta-analytics-consent' || event.key === null) location.reload();
};
onMounted(() => { start(); window.addEventListener('storage', syncChoice); });
onUnmounted(() => window.removeEventListener('storage', syncChoice));
</script>

<template>
  <section v-if="visible" class="consent-banner" role="region" aria-labelledby="consent-title" aria-describedby="consent-description">
    <button class="consent-close" type="button" aria-label="Chiudi e rifiuta i cookie statistici" @click="choose('rejected')"><InterfaceIcon name="close" /></button>
    <p class="consent-eyebrow">Le tue preferenze</p>
    <h2 id="consent-title">La tua privacy conta.</h2>
    <p v-if="preview" class="consent-preview">Anteprima locale · nessuna scelta viene salvata</p>
    <p v-if="available || preview" id="consent-description">Usiamo strumenti necessari per ricordare la tua scelta. Solo con il tuo consenso usiamo Google Analytics per capire come viene utilizzato il sito. Se chiudi questo avviso, i cookie statistici rimangono disattivati.</p>
    <p v-else id="consent-description">I cookie statistici non sono attivi. Quando saranno disponibili, potrai scegliere qui se accettarli.</p>
    <NuxtLink to="/privacy">Privacy e cookie policy</NuxtLink>
    <p v-if="storageError" role="alert">Non riusciamo a salvare la preferenza su questo dispositivo. Controlla le impostazioni di archiviazione del browser e riprova.</p>
    <div v-if="available || preview" class="consent-actions">
      <button type="button" @click="choose('rejected')">Rifiuta tutto</button>
      <button type="button" @click="choose('accepted')">Accetta tutto</button>
    </div>
    <div v-else class="consent-actions"><button type="button" @click="choose('rejected')">Chiudi</button></div>
  </section>
</template>
