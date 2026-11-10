<script setup lang="ts">
import type { EnergyPublication, EnergyYear } from '../../../shared/energy';
import type { OverlayInput } from '../../utils/history';
import EnergyBreakdown from '../molecules/EnergyBreakdown.vue';
import OverlayChart from '../molecules/OverlayChart.vue';
import TopicIllustration from '../atoms/TopicIllustration.vue';
import InterfaceIcon from '../atoms/InterfaceIcon.vue';
import { formatValue } from '../../utils/presentation';

const gwh = new Intl.NumberFormat('it-IT', { useGrouping: true, minimumFractionDigits: 1, maximumFractionDigits: 1 });

const { data } = await useFetch<EnergyPublication>('/api/energy-statistics', { key: 'province-energy' });
const years = computed(() => data.value?.years ?? []);
const first = computed(() => years.value[0]);
const latest = computed(() => years.value.at(-1));
const period = computed(() => `${first.value?.year}–${latest.value?.year}`);
const generation = computed(() => latest.value?.generation);
const difference = computed(() => {
  const year = latest.value;
  return year?.generation ? Math.round((year.generation.net - year.consumption.total) * 10) / 10 : null;
});
const renewableShare = computed(() => {
  const year = latest.value;
  return year?.generation?.gross ? year.production.total / year.generation.gross * 100 : null;
});
const percentage = new Intl.NumberFormat('it-IT', { maximumFractionDigits: 1 });

const production = [
  { key: 'wind', label: 'Eolico', color: 'var(--energy-wind)' },
  { key: 'solar', label: 'Fotovoltaico', color: 'var(--energy-solar)' },
  { key: 'hydro', label: 'Idroelettrico', color: 'var(--energy-hydro)' },
  { key: 'bioenergy', label: 'Bioenergie', color: 'var(--energy-bioenergy)' },
  { key: 'geothermal', label: 'Geotermia', color: 'var(--energy-geothermal)' },
] as const;
const consumption = [
  { key: 'industry', label: 'Industria', color: 'var(--tone-0)' },
  { key: 'services', label: 'Servizi', color: 'var(--tone-1)' },
  { key: 'domestic', label: 'Usi domestici', color: 'var(--tone-2)' },
  { key: 'agriculture', label: 'Agricoltura', color: 'var(--tone-3)' },
] as const;
const productionItems = computed(() => production.map(item => ({
  ...item, value: latest.value?.production[item.key] ?? null,
})));
const consumptionItems = computed(() => consumption.map(item => ({
  ...item, label: item.key === 'services' && latest.value?.year === 2018 ? 'Terziario' : item.label,
  value: latest.value?.consumption[item.key] ?? null,
})));

/** Carry empty years through to the plot so it never joins points across a gap. */
const timeline = computed(() => {
  if (!first.value || !latest.value) return [];
  const start = first.value.year;
  const byYear = new Map(years.value.map(row => [row.year, row]));
  return Array.from({ length: latest.value.year - start + 1 }, (_, index) => ({
    year: start + index,
    row: byYear.get(start + index),
  }));
});

function series(code: string, name: string, measure: (row: EnergyYear) => number | null): OverlayInput {
  return {
    code, name,
    values: timeline.value.map(({ year, row }) => {
      const value = row ? measure(row) : null;
      return { period: String(year), value, status: value === null ? 'missing' : 'observed' };
    }),
  };
}

const totals = computed(() => [
  generation.value
    ? series('generation-net', 'Produzione netta', row => row.generation?.net ?? null)
    : series('renewable-total', 'Produzione rinnovabile', row => row.production.total),
  series('consumption-total', 'Consumi elettrici', row => row.consumption.total),
]);
const renewableSources = computed(() => production.flatMap(item => {
  const baseline = first.value?.production[item.key];
  if (baseline == null || baseline <= 0) return [];

  const source = series(item.key, item.label, row => row.production[item.key]);
  const values = source.values.map(point => point.value === null ? point : {
    ...point,
    value: (point.value - baseline) / baseline * 100,
    detail: `${gwh.format(point.value)} GWh`,
  });
  return [{ ...source, values, color: item.color }];
}));
const renewableSourceTones = computed(() => Object.fromEntries(
  renewableSources.value.map((item, index) => [`--tone-${index}`, item.color]),
));
const sectors = computed(() => consumption.map(item => series(item.key, item.label, row =>
  item.key === 'services' && row.year === 2018 ? null : row.consumption[item.key])));
</script>

<template>
  <article v-if="latest && data" id="energia-irpinia" class="metric-story energy-story" aria-labelledby="energy-heading">
    <header class="story-heading">
      <div class="story-title">
        <div class="story-intro">
          <h3 id="energy-heading">Energia dell’Irpinia</h3>
          <p class="story-period">Provincia di Avellino · {{ latest.year }}</p>
        </div>
        <TopicIllustration topic="environment" metric="renewable-energy" />
      </div>
    </header>

    <div class="story-values story-values--multiple energy-headlines">
      <div>
        <span class="story-scope">{{ generation ? 'Elettricità prodotta (al netto)' : 'Elettricità rinnovabile prodotta' }}</span>
        <p class="story-number">{{ gwh.format(generation?.net ?? latest.production.total) }} <small>GWh</small></p>
      </div>
      <div>
        <span class="story-scope">Consumi elettrici</span>
        <p class="story-number">{{ gwh.format(latest.consumption.total) }} <small>GWh</small></p>
      </div>
    </div>

    <p v-if="difference !== null" class="story-description energy-intro">
      Nel {{ latest.year }} la provincia ha prodotto <strong v-if="difference">{{ gwh.format(Math.abs(difference)) }} GWh in {{ difference > 0 ? 'più' : 'meno' }} di quanti ne ha consumati</strong><strong v-else>tanta elettricità quanta ne ha consumata</strong>.
    </p>
    <p v-if="generation && renewableShare !== null" class="energy-mix">
      Le rinnovabili rappresentano il <strong>{{ percentage.format(renewableShare) }}% della produzione lorda provinciale</strong>.
      {{ gwh.format(latest.production.total) }} GWh da fonti rinnovabili e {{ gwh.format(generation.gross - latest.production.total) }} GWh di altra produzione.
    </p>

    <div class="story-row story-row--pair energy-composition">
      <EnergyBreakdown title="Rinnovabili per fonte" :items="productionItems" variant="donut" />
      <EnergyBreakdown title="Consumi per settore" :items="consumptionItems" variant="bars" />
    </div>

    <div v-if="years.length > 1" class="energy-histories">
      <section class="energy-history-block">
        <header class="history-context">
          <p class="eyebrow">Serie annuali · {{ period }}</p>
          <h4>Produzione e consumi nel tempo</h4>
        </header>
        <OverlayChart :series="totals" :unit="data.unit" :label="generation ? 'Produzione netta e consumi elettrici' : 'Produzione rinnovabile e consumi elettrici'" metric-id="energy-totals" lines-only note="" />
      </section>
      <section v-if="renewableSources.length" class="energy-history-block">
        <header class="history-context">
          <h4>Fonti rinnovabili · variazione dal {{ first?.year }}</h4>
        </header>
        <OverlayChart
          :series="renewableSources"
          :style="renewableSourceTones"
          unit="%"
          :label="`Variazione della produzione rinnovabile per fonte rispetto al ${first?.year}`"
          metric-id="energy-renewable-sources"
          zero-baseline
          lines-only
          signed-percent
          note=""
        />
      </section>
      <section class="energy-history-block">
        <header class="history-context">
          <h4>Come cambiano i consumi per settore</h4>
        </header>
        <OverlayChart :series="sectors" :unit="data.unit" label="Consumi elettrici per settore" metric-id="energy-sectors" zero-baseline lines-only note="" />
      </section>
    </div>

    <details class="story-source energy-method">
      <summary>Significato e fonti del dato</summary>
      <p>Dati annuali di Terna per la provincia di Avellino. Un gigawattora (GWh) equivale a un milione di kilowattora (kWh).</p>
      <ul class="energy-source-list">
        <li v-if="latest.source.generationPage">
          <a :href="`${latest.source.url}#page=${latest.source.generationPage}`" target="_blank" rel="noreferrer">Produzione totale · tavola 5 <InterfaceIcon name="arrow-up-right" /></a>
          <p>La produzione lorda comprende tutta l’elettricità generata. La produzione netta sottrae quella usata dagli impianti per funzionare.</p>
        </li>
        <li>
          <a :href="`${latest.source.url}#page=${latest.source.productionPage}`" target="_blank" rel="noreferrer">Produzione da rinnovabili · tavola 6 <InterfaceIcon name="arrow-up-right" /></a>
          <p>La tavola distingue eolico, fotovoltaico, idroelettrico, bioenergie e geotermia. Il trattino segnala una voce senza valore numerico.</p>
        </li>
        <li>
          <a :href="`${latest.source.url}#page=${latest.source.consumptionPage}`" target="_blank" rel="noreferrer">Consumi elettrici · tavola 7 <InterfaceIcon name="arrow-up-right" /></a>
          <p>I consumi sono divisi tra industria, servizi, famiglie e agricoltura. Terna conteggia a parte, nel totale della Campania, l’elettricità usata per far viaggiare i treni.</p>
        </li>
      </ul>
      <p v-if="generation"><strong>Produzione e consumi.</strong> La differenza confronta due totali annui. Nel rapporto Terna gli scambi con la rete sono riportati a livello regionale. La quota rinnovabile descrive la produzione locale lorda e il resto è calcolato per differenza.</p>
      <p><strong>Andamento per fonte.</strong> Il grafico confronta la produzione di ciascuna fonte con il proprio valore del {{ first?.year }}. Lo 0% indica lo stesso livello, i valori positivi un aumento e quelli negativi una diminuzione.</p>
      <p v-if="first?.year === 2018"><strong>Consumi dei servizi.</strong> La serie parte dal 2019. Nel 2018 Terna riporta la voce «Terziario» ({{ formatValue(first.consumption.services) }} GWh).</p>
      <template v-if="years.length > 1">
        <p><strong>Tavole Terna degli altri anni</strong></p>
        <ul class="energy-sources">
          <li v-for="item in years.slice(0, -1).reverse()" :key="item.year">
            <strong>{{ item.year }}</strong>
            <a v-if="item.source.generationPage" :href="`${item.source.url}#page=${item.source.generationPage}`" target="_blank" rel="noreferrer">Produzione totale</a>
            <a :href="`${item.source.url}#page=${item.source.productionPage}`" target="_blank" rel="noreferrer">Rinnovabili</a>
            <a :href="`${item.source.url}#page=${item.source.consumptionPage}`" target="_blank" rel="noreferrer">Consumi</a>
          </li>
        </ul>
      </template>
    </details>
  </article>
</template>

<style scoped>
.energy-story {
  --energy-wind: var(--tone-0);
  --energy-solar: var(--tone-1);
  --energy-hydro: var(--tone-2);
  --energy-bioenergy: var(--tone-3);
  --energy-geothermal: var(--muted);
  margin-bottom: 1rem;
}
.energy-headlines { max-width: 34rem; margin-bottom: 1.5rem; }
.territory-page .energy-headlines .story-number { font-size: clamp(1.65rem, 3vw, 2.5rem); white-space: nowrap; }
.energy-mix { margin: 0 0 1rem; color: var(--muted); font-size: .87rem; line-height: 1.6; }
.energy-composition { gap: 1.5rem 2.25rem; }
.energy-histories { margin-top: 1.5rem; }
.energy-history-block { padding-block: 1.25rem; border-top: 1px solid var(--line); }
.energy-history-block .history-context { margin: 0; padding: 0 0 .5rem; border: 0; }
.energy-history-block .history-context h4 { margin: 0; font-size: clamp(1rem, 2vw, 1.3rem); }
.energy-history-block .history-context p { margin: .3rem 0 0; }
.portal-main .energy-method p { font-size: .8rem; }
.energy-source-list > li { margin: 0; }
.energy-source-list p { margin: .25rem 0 0; }
.energy-source-list { display: grid; gap: .65rem 1.5rem; list-style: none; padding: 0; margin: .85rem 0 1rem; }
.energy-source-list a { display: inline-flex; align-items: center; gap: .35rem; font-size: .83rem; font-weight: 700; }
.energy-source-list svg { width: .8rem; height: .8rem; flex: 0 0 auto; }
.energy-sources { list-style: none; margin: .35rem 0; padding: 0; }
.energy-sources li { display: flex; flex-wrap: wrap; gap: .2rem 1rem; padding: .35rem 0; }
.energy-sources li strong { font-variant-numeric: tabular-nums; }
@media (min-width: 761px) {
  .energy-headlines { width: calc(100% - clamp(150px, 21vw, 240px)); min-height: 70px; }
  .energy-source-list { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .energy-story .story-heading { padding-top: .4rem; }
}
</style>
