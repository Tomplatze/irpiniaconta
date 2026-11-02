import type { Dataset, Indicator, ValueStatus } from '../../shared/types';

const datasetTitles: Record<string, string> = {
  istat_demography: 'Popolazione e demografia',
  mef_irpef: 'Redditi dichiarati',
  infocamere_units: 'Imprese e unità locali',
  ispra_soil: 'Consumo di suolo',
  istat_agriculture: 'Censimento dell’agricoltura',
};

const datasetDescriptions: Record<string, string> = {
  istat_demography: 'Residenti per età e sesso. La popolazione al 1° gennaio 2026 è una stima ISTAT, distinta dai risultati definitivi del censimento.',
  mef_irpef: 'Dichiarazioni IRPEF comunali. Il reddito medio è calcolato per dichiarante; non è il reddito disponibile di ogni abitante.',
  infocamere_units: 'Le unità locali descrivono le sedi operative delle imprese. La distribuzione pubblica verificata riguarda la Toscana.',
  ispra_soil: 'Superficie artificiale e variazione netta. L’edizione 2025 del rapporto contiene misure del 2024.',
  istat_agriculture: 'Censimento 2020, anno agricolo 2019/2020. Aziende e superfici sono attribuite alla sede dell’azienda: non descrivono tutta la superficie agricola entro i confini del comune.',
};

const definitions: Record<string, string> = {
  population: 'Stima dei residenti al 1° gennaio, entrambi i sessi. Il totale viene letto dalla riga ufficiale ISTAT.',
  population_65_plus_share: 'Residenti con almeno 65 anni sul totale della popolazione stimata, in percentuale.',
  irpef_taxpayers: 'Numero di contribuenti IRPEF nel comune, riferito all’anno d’imposta indicato.',
  irpef_income_declarants: 'Numero di dichiaranti con reddito complessivo: è il denominatore del reddito medio.',
  irpef_income_total: 'Somma nominale del reddito complessivo dichiarato nel comune, in euro.',
  irpef_income_mean: 'Reddito complessivo dichiarato diviso per il numero dei relativi dichiaranti. Non è una misura per residente.',
  soil_consumed_ha: 'Superficie artificiale complessiva osservata nel territorio comunale, in ettari.',
  soil_consumed_pct: 'Superficie artificiale rispetto alla superficie totale del comune, in percentuale.',
  soil_net_change_ha: 'Incremento di suolo consumato tra 2023 e 2024, al netto delle superfici ripristinate. Può essere negativo.',
  active_local_units: 'Numero di unità locali attive nel comune. I dati per l’Irpinia non sono stati acquisiti.',
  agricultural_holdings: 'Aziende del censimento agricolo 2020, attribuite al comune in cui ha sede l’azienda.',
  utilised_agricultural_area: 'Superficie agricola utilizzata nell’anno 2019/2020, attribuita al comune della sede aziendale. I terreni possono trovarsi anche in altri comuni.',
};

/** Format source periods without confusing report editions with observation years. */
export function formatPeriod(period: string | null): string {
  if (!period) return 'Periodo non disponibile';
  if (/^\d{4}$/.test(period)) return period;
  if (/^\d{4}-\d{2}$/.test(period)) return new Intl.DateTimeFormat('it-IT', {
    month: 'short', year: 'numeric', timeZone: 'UTC',
  }).format(new Date(`${period}-01T12:00:00Z`));
  const date = new Date(`${/^\d{4}-\d{2}$/.test(period) ? period+'-01' : period}T12:00:00Z`);
  return Number.isNaN(date.getTime()) ? period : new Intl.DateTimeFormat('it-IT', {
    day: 'numeric', month: 'short', year: 'numeric', timeZone: 'Europe/Rome',
  }).format(date);
}

/** Format acquisition timestamps consistently during server and browser rendering. */
export function formatDate(value: string): string {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? 'Non disponibile' : new Intl.DateTimeFormat('it-IT', {
    day: 'numeric', month: 'long', year: 'numeric', timeZone: 'Europe/Rome',
  }).format(date);
}

/** Use local display rounding while preserving the original values in storage. */
export function formatValue(value: number | null, unit = ''): string {
  if (value === null) return '—';
  return new Intl.NumberFormat('it-IT', {
    maximumFractionDigits: ['persons', 'local units', 'holdings', 'heads'].includes(unit) ? 0 : unit === 'km²' ? 3 : 2,
  }).format(value);
}

/** Shorten large funding headlines; exact original values remain in source-backed charts and evidence. */
export function formatHeadlineValue(value: number | null, unit = ''): string {
  if (value === null || unit !== 'EUR' || Math.abs(value) < 1_000_000) return formatValue(value,unit);
  const divisor = Math.abs(value) >= 1_000_000_000 ? 1_000_000_000 : 1_000_000;
  return `${formatValue(value/divisor)} ${divisor===1_000_000_000 ? 'miliardi' : 'milioni'}`;
}

/** Translate measurement units without changing their statistical meaning. */
export function unitLabel(unit: string): string {
  return ({ persons: 'persone', 'local units': 'unità locali', holdings: 'aziende',
    EUR: '€', 'EUR/declarant': '€/dichiarante', 'EUR/resident': '€/abitante', 'EUR/person': '€/persona', hectares: 'ha', ha: 'ha', heads: 'capi', households: 'famiglie', beds: 'posti letto', facilities: 'strutture', projects: 'progetti', 'kg/person': 'kg/abitante', days: 'giorni', 'mapped sites': 'elementi mappati', 'listed places': 'luoghi', 'listed records': 'voci', 'school units': 'sedi', locations: 'sedi', vehicles: 'veicoli', dwellings: 'abitazioni' } as Record<string, string>)[unit] ?? unit;
}

/** Explicit absence labels prevent an unavailable value from looking like zero. */
export function statusLabel(status: ValueStatus): string {
  return { observed: 'Dato disponibile', missing: 'Dato mancante', suppressed: 'Dato riservato',
    unavailable: 'Non disponibile' }[status];
}

/** Supply editorial Italian names, retaining unknown source names verbatim. */
export function datasetTitle(dataset: Dataset): string {
  return datasetTitles[dataset.id] ?? dataset.name;
}

/** Describe the verified source meaning without publishing technical machinery. */
export function datasetDescription(dataset: Dataset): string {
  return datasetDescriptions[dataset.id] ?? dataset.name;
}

/** Keep exact technical source notes readable even when metadata uses a list. */
export function sourceNotes(dataset: Dataset): string[] {
  return Array.isArray(dataset.notes) ? dataset.notes.filter((note): note is string => typeof note === 'string') : [dataset.notes];
}

/** Provide the source-qualified metric definition used next to the chart. */
export function indicatorDescription(indicator: Indicator): string {
  return definitions[indicator.id] ?? indicator.definition;
}

/** State the practical cause of a blocked integration; retain details separately. */
export function blockerSummary(dataset: Dataset): string {
  if (dataset.id === 'infocamere_units') {
    return 'Il file verificato non contiene comuni della provincia di Avellino. Occorre una distribuzione comunale autorizzata per l’Irpinia; anche la licenza va chiarita.';
  }
  if (dataset.id === 'istat_agriculture') {
    return 'Il servizio ufficiale non ha restituito una distribuzione comunale acquisibile e verificabile. L’adapter è predisposto; nessun valore è stato inserito.';
  }
  return 'L’acquisizione non ha superato la verifica della fonte. Il dettaglio del blocco è disponibile qui sotto.';
}

/** Summarize current observed coverage separately for each indicator. */
export function coverageLabel(indicator: Indicator, municipalityCount: number): string {
  return `${indicator.observed_count} / ${municipalityCount} comuni`;
}
