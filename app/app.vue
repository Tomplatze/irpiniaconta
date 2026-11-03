<script setup lang="ts">
import InterfaceIcon from '~/components/atoms/InterfaceIcon.vue';
import creatorArtwork from './assets/illustrations/project-creator.webp';
import AnalyticsConsent from './components/organisms/AnalyticsConsent.vue';
import { HEALTH_PUBLICATION_READY } from './utils/healthPublication';
const route = useRoute();
const healthAvailable = import.meta.dev || HEALTH_PUBLICATION_READY;
const { openPreferences } = useAnalyticsConsent();
const { progress, isLoading } = useLoadingIndicator();
const siteUrl = 'https://irpiniaconta.it';
const canonicalUrl = computed(() => {
  const url = new URL(route.path, siteUrl);
  if (route.path.startsWith('/sezioni/') && typeof route.query.code === 'string') url.searchParams.set('code', route.query.code);
  return url.toString();
});
const socialImage = `${siteUrl}/images/social-preview.jpg`;
useHead({ link: [{ rel: 'canonical', href: canonicalUrl }] });
useSeoMeta({
  description: 'Esplora dati, mappe e grafici sui 118 comuni dell’Irpinia: persone, economia, ambiente e servizi.',
  ogTitle: 'IrpiniaConta — I numeri del territorio',
  ogDescription: 'Esplora dati, mappe e grafici sui 118 comuni dell’Irpinia: persone, economia, ambiente e servizi.',
  ogType: 'website', ogSiteName: 'IrpiniaConta', ogLocale: 'it_IT', ogUrl: canonicalUrl,
  ogImage: socialImage, ogImageType: 'image/jpeg', ogImageWidth: 1200, ogImageHeight: 675,
  ogImageAlt: 'IrpiniaConta: dati pubblici, persone e territori dell’Irpinia.',
  twitterCard: 'summary_large_image', twitterTitle: 'IrpiniaConta — I numeri del territorio',
  twitterDescription: 'Esplora dati, mappe e grafici sui 118 comuni dell’Irpinia: persone, economia, ambiente e servizi.',
  twitterImage: socialImage, twitterImageAlt: 'IrpiniaConta: dati pubblici, persone e territori dell’Irpinia.',
});
</script>
<template>
  <div class="atlas-app">
    <div class="page-loading" :class="{ 'is-visible': isLoading }" aria-hidden="true"><span :style="{ transform: `scaleX(${progress / 100})` }" /></div>
    <div class="page-loading-status" role="status" aria-live="polite"><span v-if="isLoading">Caricamento della pagina…</span></div>
    <a class="skip-link" href="#contenuto">Vai al contenuto</a>
    <header class="portal-header">
      <NuxtLink to="/" class="brand" aria-label="IrpiniaConta Beta, homepage"><span class="conta-mark" aria-hidden="true"><i /><i /><i /><i /></span><span>irpinia<strong>conta</strong><small>.it</small></span><span class="brand-beta">Beta</span></NuxtLink>
      <nav aria-label="Navigazione principale"><NuxtLink to="/" :class="{'is-active':route.path.startsWith('/sezioni/')}">L’Irpinia</NuxtLink><NuxtLink to="/comuni">I comuni</NuxtLink><NuxtLink to="/confronta">Confronta</NuxtLink><NuxtLink v-if="healthAvailable" to="/salute" class="health-nav-link"><InterfaceIcon name="heart-pulse" />Salute in Irpinia</NuxtLink></nav>
      <div id="topic-navigation-slot" class="topic-navigation-slot" />
    </header>
    <main id="contenuto" class="portal-main" tabindex="-1"><NuxtPage :transition="{ name: 'page-enter', mode: 'default' }" /></main>
    <aside class="project-notice" aria-labelledby="project-notice-title">
      <div class="project-notice__intro"><p class="project-notice__eyebrow">Trasparenza del progetto</p><h2 id="project-notice-title">Un progetto indipendente, in fase beta.</h2><img class="project-notice__art" :src="creatorArtwork" alt="" aria-hidden="true" loading="lazy" decoding="async" /></div>
      <div class="project-notice__content"><p>IrpiniaConta è un progetto amatoriale, realizzato nel tempo libero. Non è un sito istituzionale e le sue elaborazioni non sono dati ufficiali.</p><p>Le informazioni provengono dalle fonti indicate, ma possono contenere errori, omissioni o dati non aggiornati. Per usi ufficiali o decisioni importanti consulta sempre le fonti originali.</p><p>Il codice del progetto è destinato alla pubblicazione open source con <a href="https://opensource.org/license/mit" target="_blank" rel="noopener noreferrer">licenza MIT</a>. I dati e i contenuti di terzi mantengono le rispettive condizioni d’uso.</p><p>Per realizzare il progetto e analizzare i dati sono stati usati anche strumenti e agenti di intelligenza artificiale, i cui risultati possono contenere errori.</p><NuxtLink to="/raccolta">Consulta le fonti e i dati originali <InterfaceIcon name="arrow-up-right" /></NuxtLink></div>
    </aside>
    <footer class="portal-footer"><div class="footer-brand">irpinia<strong>conta</strong>.it<p>Il territorio, attraverso i dati.</p></div><nav aria-label="Informazioni sul sito"><NuxtLink to="/raccolta#catalogo-fonti">Catalogo delle fonti</NuxtLink><NuxtLink to="/privacy">Privacy e cookie</NuxtLink><button type="button" class="footer-preferences" @click="openPreferences">Preferenze cookie</button></nav><div class="footer-credit"><a class="footer-open-source" href="https://github.com/Tomplatze/irpiniaconta" target="_blank" rel="noopener noreferrer"><svg viewBox="0 0 16 16" width="18" height="18" fill="currentColor" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38v-1.49c-2.23.49-2.69-1.08-2.69-1.08-.36-.92-.89-1.16-.89-1.16-.73-.5.05-.49.05-.49.8.06 1.22.82 1.22.82.71 1.21 1.87.86 2.33.66.07-.52.28-.86.51-1.06-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82A7.65 7.65 0 0 1 8 3.74c.68 0 1.36.09 2 .27 1.53-1.03 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.28.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48v2.32c0 .21.15.46.55.38A8 8 0 0 0 8 0Z"/></svg> Progetto open source · MIT <small>Repository su GitHub</small></a></div><div class="footer-credit footer-credit--author"><span>Un progetto di</span><a href="https://francescobianco.it" target="_blank" rel="noopener noreferrer">Francesco Bianco</a></div></footer>
    <AnalyticsConsent />
  </div>
</template>
