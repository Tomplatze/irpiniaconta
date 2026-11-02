import type { SourceEntry } from '../../shared/catalogue';
import type { CollectionScope } from '../../shared/collection';

/** Keep collection availability distinct from normalized product integration. */
export const collectionStatusLabels: Record<CollectionScope['status'], string> = {
  integrated: 'Già nelle sezioni', collected: 'Dati raccolti', alternative: 'Alternativa gratuita',
  partial: 'Disponibilità parziale', not_collected: 'Da completare',
};

/** Preserve the source registry's four integration outcomes. */
export const sourceStatusLabels: Record<SourceEntry['status'], string> = {
  ready: 'Dati disponibili', blocked: 'Dati non disponibili', pending: 'Da verificare', restricted: 'Accesso limitato',
};

/** Reachability describes a source page, independently of usable data. */
export function sourceReachability(value: string | null): string {
  return value === 'reachable' ? 'Pagina della fonte raggiungibile' : value === 'failed' ? 'Non è stato possibile raggiungere la pagina della fonte' : 'Pagina della fonte non verificata';
}

/** Translate known registry geography labels while preserving unfamiliar source terms. */
export function sourceGeography(value: string): string {
  const labels: Record<string, string> = {
    municipality: 'Dettaglio comunale', province: 'Dettaglio provinciale',
    region: 'Dettaglio regionale', national: 'Copertura nazionale',
  };
  return labels[value] ?? value;
}

/** Preserve license identifiers and conflicting claims while translating their context. */
export function licenseDescription(value: string): string {
  const descriptions: Record<string, string> = {
    'CC-BY-4.0 (ISTAT default unless otherwise indicated)': 'CC BY 4.0 (licenza ISTAT, salvo diversa indicazione)',
    'CC BY 4.0 (ISTAT default)': 'CC BY 4.0 (licenza ISTAT)',
    'Conflicting metadata: CC BY 4.0 (dati.gov.it resource), CC BY-SA (Tuscany CKAN package)': 'Indicazioni discordanti: CC BY 4.0 nella risorsa dati.gov.it e CC BY-SA nel catalogo della Regione Toscana. La licenza è da chiarire.',
    'CC BY 3.0 IT (official landing page)': 'CC BY 3.0 IT (indicata nella pagina ufficiale)',
    'CC BY 4.0 (specific dataset RDF)': 'CC BY 4.0 (indicata nei metadati della raccolta)',
  };
  return descriptions[value] ?? value;
}

/** Summarize original periods without manufacturing an observation year. */
export function collectionPeriods(values: string[]): string {
  const labels = values.map(value => value.startsWith('undated') ? 'Periodo non dichiarato dalla fonte'
    : value === 'mixed_vintages' ? 'Basi temporali diverse'
      : /^20\d{4}$/.test(value) ? `${value.slice(0, 4)}/${value.slice(4)}` : value);
  return labels.length > 5 ? `${labels[0]} … ${labels.at(-1)} · ${labels.length} periodi` : labels.join(', ') || 'Periodo non dichiarato';
}

/** Replace internal collection notes with source-specific public explanations. */
export function collectionSummary(id: string, summary: string): string {
  const descriptions: Record<string, string> = {
    'ECO-01': 'Sedi delle imprese e persone che vi lavorano, suddivise per tipo di attività, secondo ISTAT.',
    'ECO-04': 'Dati su sedi delle imprese e addetti; il censimento economico completo richiede ulteriori approfondimenti.',
    'ECO-05': 'Statistiche comunali ISTAT e altre informazioni pubblicate dalle Camere di commercio.',
    'ECO-09': 'Il registro completo delle imprese non è disponibile in questa raccolta come insieme di dati comunali a libero accesso.',
    'PA-02': 'Sono disponibili due anni di bilanci, 2024 e 2025. I bilanci più vecchi non sono ancora presenti nella raccolta.',
    'PA-03': 'Gli incassi e i pagamenti annuali sono presenti nei bilanci. I dati del servizio SIOPE non sono disponibili in questa raccolta.',
    'INV-03': 'Sono disponibili informazioni sulle opere finanziate dalle politiche di coesione; l’elenco completo delle opere pubbliche non è ancora disponibile.',
    'INV-06': 'Sono presenti informazioni sui soggetti coinvolti in OpenCUP; altri progetti sono disponibili tramite PNRR e OpenCoesione.',
    'AGR-06': 'Informazioni sull’agricoltura biologica dal censimento 2020, presenti per 114 comuni.',
    'AGR-07': 'Censimenti agricoli precedenti: i confronti devono tenere conto delle fusioni tra comuni.',
    'AMB-08': 'Dati CORINE 2018 sulle coperture del territorio, tra cui aree urbane, coltivazioni e boschi.',
    'CLI-01': 'È disponibile una ricostruzione meteorologica alternativa, distinta dalle misurazioni delle centraline SCIA.',
    'CLI-02': 'Dati ERA5-Land, una ricostruzione meteorologica resa disponibile tramite Open-Meteo.',
    'CLI-03': 'Per tutti i comuni è disponibile una ricostruzione meteorologica. I dati storici delle stazioni regionali non sono presenti in questa raccolta.',
    'CLI-04': 'Sono disponibili temperature e piogge giornaliere; non tutti questi dati sono mostrati negli indicatori dell’atlante.',
    'CUL-09': 'Informazioni sui centri storici e sul paesaggio presenti nella cartografia consultata.',
    'MOB-03': 'Binari e stazioni presenti nelle mappe consultate; la presenza sulla mappa non conferma che siano in servizio.',
    'MOB-04': 'Fermate presenti nelle mappe consultate; orari e linee non sono ancora disponibili nella raccolta.',
    'MOB-06': 'Dati comunali sugli spostamenti quotidiani per gli anni 2018 e 2019.',
    'MOB-08': 'Le quotazioni immobiliari sono consultabili presso la fonte; non sono disponibili in questa raccolta come dati scaricabili per tutti i comuni.',
  };
  if (descriptions[id]) return descriptions[id]!;
  return summary === 'Dati acquisiti: dettaglio, anni e copertura disponibili nell’inventario.'
    ? 'Di seguito trovi gli anni disponibili e i comuni presenti nella raccolta.' : summary;
}

/** Summarize known limitations without publishing internal error messages. */
export function collectionLimitation(id: string): string {
  const limitations: Record<string, string> = {
    'ECO-09': 'I dati statistici ISTAT descrivono le attività nel loro insieme e non sostituiscono le informazioni sulle singole imprese.',
    'PA-03': 'I pagamenti e gli incassi annuali dei bilanci non sostituiscono i dati mensili di SIOPE.',
    'AGR-08': 'Non sono disponibili dati verificati sulla produzione annuale per ciascun comune.',
    'CLI-03': 'La ricostruzione meteorologica e le misure delle stazioni sono informazioni diverse.',
    'MOB-08': 'Il numero di abitazioni censite non sostituisce le quotazioni di mercato.',
  };
  return limitations[id] ?? 'Alcune informazioni di questa fonte non sono disponibili nella raccolta.';
}
