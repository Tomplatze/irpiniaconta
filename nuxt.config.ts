export default defineNuxtConfig({
  compatibilityDate: '2026-10-12',
  devtools: { enabled: false },
  modules: ['nuxt-gtag'],
  gtag: { initMode: 'manual' },
  css: ['~/assets/css/main.css', '~/assets/css/fonts.css', '~/assets/css/technical.css', '~/assets/css/collection.css', '~/assets/css/sections.css', '~/assets/css/territory.css', '~/assets/css/charts.css', '~/assets/css/supporting-pages.css', '~/assets/css/refinement.css', '~/assets/css/map-readout.css', '~/assets/css/demographic-flows.css', '~/assets/css/municipal-stories.css', '~/assets/css/illustration-layout.css', '~/assets/css/privacy.css'],
  typescript: { strict: true, typeCheck: false },
  runtimeConfig: { databaseReadUrl: '', public: { analyticsId: '', analyticsPolicyReady: false } },
  app: { head: {
    htmlAttrs: { lang: 'it' },
    title: 'IrpiniaConta — I numeri del territorio',
    meta: [{ name: 'description', content: 'Numeri e informazioni dalle fonti pubbliche per conoscere e confrontare i 118 comuni dell’Irpinia.' }],
  } },
});
