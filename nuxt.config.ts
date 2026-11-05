import { HEALTH_PUBLICATION_READY } from './app/utils/healthPublication';

export default defineNuxtConfig({
  compatibilityDate: '2026-10-12',
  hooks: {
    'pages:extend'(pages) {
      if (process.env.NODE_ENV !== 'production' || HEALTH_PUBLICATION_READY) return;
      const healthIndex = pages.findIndex(page => page.path === '/salute');
      if (healthIndex !== -1) pages.splice(healthIndex, 1);
    },
  },
  devtools: { enabled: false },
  modules: ['nuxt-gtag'],
  gtag: { initMode: 'manual' },
  css: ['~/assets/css/main.css', '~/assets/css/fonts.css', '~/assets/css/technical.css', '~/assets/css/collection.css', '~/assets/css/sections.css', '~/assets/css/territory.css', '~/assets/css/charts.css', '~/assets/css/supporting-pages.css', '~/assets/css/refinement.css', '~/assets/css/map-readout.css', '~/assets/css/demographic-flows.css', '~/assets/css/municipal-stories.css', '~/assets/css/illustration-layout.css', '~/assets/css/privacy.css', '~/assets/css/page-loading.css', '~/assets/css/navigation.css'],
  typescript: { strict: true, typeCheck: false },
  runtimeConfig: { databaseReadUrl: '', publicationMode: 'snapshot', public: { analyticsId: '', analyticsPolicyReady: false } },
  app: { head: {
    htmlAttrs: { lang: 'it' },
    title: 'IrpiniaConta — I numeri del territorio',
    meta: [
      { name: 'description', content: 'Numeri e informazioni dalle fonti pubbliche per conoscere e confrontare i 118 comuni dell’Irpinia.' },
      { name: 'theme-color', content: '#f5f3eb' },
    ],
    link: [
      { rel: 'icon', href: '/favicon.ico', sizes: 'any' },
      { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
      { rel: 'icon', type: 'image/png', sizes: '32x32', href: '/favicon-32x32.png' },
      { rel: 'apple-touch-icon', sizes: '180x180', href: '/apple-touch-icon.png' },
      { rel: 'manifest', href: '/site.webmanifest' },
    ],
  } },
});
