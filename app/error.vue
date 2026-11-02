<script setup lang="ts">
import type { NuxtError } from '#app';

defineProps<{ error: NuxtError }>();
</script>

<template>
  <main class="error-page">
    <div>
      <p class="error-brand">irpinia<strong>conta</strong>.it <span>Beta</span></p>
      <h1>{{ error.statusCode === 404 ? 'Questa pagina non è disponibile.' : 'Non riusciamo a mostrare questa pagina.' }}</h1>
      <p>{{ error.statusCode === 404 ? 'Il collegamento potrebbe essere cambiato o la pagina potrebbe non esistere più.' : 'Si è verificato un problema. Riprova tra qualche momento.' }}</p>
      <button type="button" @click="clearError({ redirect: '/' })">Torna alla pagina iniziale</button>
    </div>
  </main>
</template>

<style scoped>
.error-page { min-height: 100vh; display: grid; align-items: center; padding: 2rem; background: #f3f2e9; color: #123e32; }
.error-page > div { width: min(100%, 42rem); margin: 0 auto; }
.error-brand { margin-bottom: 3rem; font-size: 1.5rem; }
.error-brand span { margin-left: .5rem; font-size: .8rem; }
.error-page h1 { font-size: clamp(2rem, 5vw, 3.5rem); line-height: 1.1; }
.error-page p { line-height: 1.6; }
.error-page button { margin-top: 1.5rem; padding: .9rem 1.2rem; border: 0; border-radius: .4rem; background: #174c3d; color: #fff; font: inherit; cursor: pointer; }
.error-page button:focus-visible { outline: 3px solid #bf5e3b; outline-offset: 3px; }
</style>
