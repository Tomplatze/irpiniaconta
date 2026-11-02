/** Public explanations keep the scope and limitations of the source data. */
export const chapterDescriptions: Record<string, string> = {
  demography: 'Quante persone vivono nel territorio, come cambiano le famiglie e come nascite, decessi e trasferimenti incidono sulla popolazione.',
  economy: 'Redditi dichiarati, sedi di attività economiche, persone che vi lavorano e possibilità di accoglienza per i visitatori.',
  administration: 'Alcune informazioni sulle risorse dei comuni: quanto spendono per i servizi e quanto viene loro assegnato dal Fondo di solidarietà comunale.',
  investments: 'Progetti e finanziamenti che interessano il territorio: dal PNRR alle politiche di coesione e ai servizi digitali dei comuni.',
  agriculture: 'Aziende, coltivazioni e allevamenti: uno sguardo ai terreni utilizzati, al biologico e agli animali censiti.',
  environment: 'Come cambia il territorio, quanto suolo è occupato da superfici artificiali e come vengono gestiti i rifiuti urbani.',
  climate: 'Temperature e giornate molto calde o fredde, ricostruite a partire da un punto di riferimento per ciascun comune.',
  culture: 'Castelli, centri storici, musei e biblioteche presenti nei cataloghi consultati. Gli elenchi possono non essere completi.',
  services: 'Scuole statali, servizi per la prima infanzia, farmacie e livelli di istruzione degli abitanti.',
  mobility: 'Auto registrate, abitazioni e spostamenti quotidiani per andare a scuola o al lavoro.',
};

const metricDescriptions: Record<string, string> = {
  population: 'Il numero di persone che, secondo la stima ISTAT, risiedono nel territorio al 1° gennaio. È una stima e va letta separatamente dai censimenti.',
  resident_population_history: 'Il numero di residenti al 31 dicembre negli anni per cui la fonte mette a disposizione i dati.',
  natural_balance: 'La differenza tra le persone nate e quelle decedute nell’anno. Un numero negativo indica che i decessi sono stati più delle nascite.',
  foreign_migration_balance: 'La differenza tra chi è arrivato dall’estero e chi si è trasferito all’estero nell’anno. Non comprende gli spostamenti tra comuni italiani.',
  foreign_residents: 'Le persone residenti che non hanno la cittadinanza italiana, secondo la stima ISTAT al 1° gennaio. Il dato non indica quante persone sono nate all’estero o sono arrivate durante l’anno.',
  population_65_plus_share: 'La percentuale di abitanti che hanno almeno 65 anni, calcolata sulla popolazione stimata.',
  private_households: 'Il numero di famiglie registrate all’anagrafe al 31 dicembre. Non comprende le convivenze collettive, come alcune strutture residenziali. I dati del 2018 e 2019 non sono mostrati: la fonte riporta valori con decimali che richiedono una verifica.',
  irpef_income_mean: 'Il reddito complessivo dichiarato, diviso per il numero di persone che hanno presentato una dichiarazione con reddito. Non rappresenta il reddito di ogni abitante e non tiene conto dell’aumento dei prezzi.',
  asia_local_units: 'Il numero di sedi operative delle imprese attive, come negozi, laboratori o uffici. Un’impresa può avere più sedi.',
  asia_employees: 'Il numero medio annuo di addetti nelle sedi operative delle imprese attive, secondo il registro statistico ISTAT.',
  tourism_beds: 'I posti letto disponibili nelle strutture ricettive considerate da ISTAT, come alberghi e altre strutture. Non indica quante persone vi hanno soggiornato. Sono esclusi i dati dei vecchi comuni che non è stato possibile associare con certezza ai comuni attuali.',
  tourism_facilities: 'Il numero di alberghi e altre strutture ricettive censite da ISTAT. Non indica quanti visitatori sono arrivati o quante camere sono occupate.',
  municipal_service_spending: 'La spesa per i servizi e le funzioni comunali considerati da OpenCivitas. Non comprende necessariamente tutte le spese del bilancio; i valori riservati o segnalati come anomali non sono mostrati.',
  admin_historic_spending_per_person: 'La spesa per le funzioni amministrative considerate da OpenCivitas, rapportata al numero di abitanti. Il valore per l’Irpinia è quello centrale tra i comuni con dato, non la spesa media provinciale per abitante.',
  solidarity_fund: 'La somma assegnata ai comuni attraverso il Fondo di solidarietà comunale. È l’importo calcolato dalla fonte: non indica necessariamente quanto è stato effettivamente incassato.',
  pnrr_projects: 'Il numero di progetti del Piano nazionale di ripresa e resilienza (PNRR) associati al territorio. Nel totale dell’Irpinia un progetto che riguarda più comuni è contato una sola volta.',
  cohesion_projects: 'I progetti delle politiche di coesione presenti nella raccolta OpenCoesione e associati al territorio. Le date di aggiornamento delle schede non descrivono l’andamento dei progetti nel tempo.',
  digital_allocated_eur: 'L’importo dei finanziamenti assegnati o erogati alle candidature comunali per i servizi digitali. Non indica quanto è già stato speso.',
  agricultural_holdings: 'Il numero di aziende agricole con sede nel territorio, secondo il censimento indicato. Il confronto con i censimenti precedenti è mostrato separatamente.',
  utilised_agricultural_area: 'La superficie utilizzata dalle aziende agricole che hanno sede nel territorio, misurata in ettari. I terreni possono trovarsi anche in comuni diversi da quello della sede.',
  vineyard_area: 'Gli ettari di vigneto delle aziende agricole con sede nel territorio. Il dato riguarda la superficie, non la quantità di vino prodotta.',
  olive_area: 'Gli ettari di oliveto delle aziende agricole con sede nel territorio. Il dato riguarda la superficie, non la quantità di olio prodotta.',
  soil_consumed_ha: 'La superficie occupata da coperture artificiali, come edifici, strade, parcheggi anche non pavimentati e cantieri. È il totale presente nell’anno indicato, non il solo terreno trasformato in quell’anno.',
  soil_net_change_ha: 'Il cambiamento annuale del suolo consumato: alle nuove superfici artificiali si sottraggono quelle ripristinate. Il risultato può essere negativo. Sono esclusi gli aumenti riferiti a più anni insieme.',
  soil_consumed_pct: 'La percentuale del territorio comunale occupata da superfici artificiali. Per l’Irpinia è mostrato il valore centrale tra i comuni con dato, non la percentuale dell’intera provincia.',
  waste_separate_share: 'La percentuale dei rifiuti urbani raccolta separatamente. Il dato per l’Irpinia è calcolato sui rifiuti dei soli comuni per cui sono disponibili valori validi; i dati che sommano più comuni non sono attribuiti ai singoli territori.',
  waste_per_person: 'I chilogrammi di rifiuti urbani prodotti in un anno, divisi per il numero di abitanti indicato dalla stessa fonte ISPRA.',
  annual_temperature: 'La temperatura media annua stimata in un punto di riferimento del comune. È una ricostruzione meteorologica, non la misura di una centralina né la media di tutto il territorio comunale. Prima del 2025 sono disponibili solo dieci punti di riferimento per tutta l’Irpinia.',
  hot_days: 'Il numero di giorni in cui la temperatura massima stimata in un punto di riferimento del comune ha raggiunto almeno 30 °C. Non descrive necessariamente ogni zona del comune.',
  frost_days: 'Il numero di giorni in cui la temperatura minima stimata in un punto di riferimento del comune è scesa sotto 0 °C. Non descrive necessariamente ogni zona del comune.',
  fortified_sites: 'Torri, castelli e fortificazioni presenti nella mappa provinciale consultata. La fonte non indica l’anno del rilievo e l’elenco potrebbe non essere completo.',
  historic_centres: 'Elementi relativi ai centri storici presenti nella mappa provinciale. Più elementi possono riferirsi allo stesso centro; la fonte non indica l’anno del rilievo e l’elenco potrebbe non essere completo.',
  cultural_places: 'Musei e luoghi della cultura presenti nel catalogo del Ministero della Cultura consultato. La fonte non indica il periodo dei dati e l’elenco potrebbe non essere completo.',
  province_libraries_listed_records: 'Biblioteche presenti nel catalogo provinciale consultato. L’elenco potrebbe non essere completo e la data riportata non indica quando ogni biblioteca è stata aperta o aggiornata.',
  state_school_sites: 'Le sedi scolastiche indicate nell’elenco del Ministero dell’Istruzione per l’anno scolastico mostrato. Un codice scolastico non corrisponde necessariamente a un edificio distinto; il numero non indica gli alunni.',
  nursery_coverage: 'La percentuale di bambini tra 0 e 2 anni che usufruiscono dei servizi di asilo nido, rispetto ai residenti della stessa età. Non indica il numero di posti disponibili. Per l’Irpinia è mostrato il valore centrale tra i comuni con dato.',
  pharmacy_location_count: 'Le sedi presenti nell’elenco del Ministero della Salute. Il dato non indica i turni, gli orari o se una farmacia sia aperta al momento della consultazione.',
  graduate_residents: 'Le persone residenti di almeno 9 anni che hanno una laurea di primo livello o un titolo universitario superiore, al 31 dicembre.',
  registered_cars: 'Le autovetture registrate nel territorio secondo ACI. Il dato non misura il traffico sulle strade.',
  empty_dwellings: 'Le abitazioni che risultano non occupate al 31 dicembre. Non sono necessariamente abbandonate o disponibili sul mercato.',
  all_dwellings: 'Le abitazioni convenzionali censite al 31 dicembre, occupate e non occupate.',
  daily_commuters: 'Le persone residenti che si spostano ogni giorno per studio o lavoro, all’interno del comune o verso un altro comune.',
};

/** Fall back to the published wording for indicators added in the future. */
export function metricDescription(id: string, fallback: string): string {
  return metricDescriptions[id] ?? fallback;
}

/** Explain aggregation without changing the calculation or its source. */
export function summaryDescription(label: string): string {
  const descriptions: Record<string, string> = {
    'Totale dei comuni con dato': 'Totale dei comuni per cui il dato è disponibile',
    'Media ponderata con il denominatore della fonte': 'Media che tiene conto del peso di ciascun comune',
    'Media dei punti di campionamento': 'Media dei punti di riferimento considerati',
    'Mediana dei comuni con dato': 'Valore centrale tra i comuni con dato',
    'Elementi distinti nella raccolta': 'Totale dei progetti distinti nella raccolta',
    'Ultimo periodo disponibile della fonte': 'Ultimo dato disponibile',
  };
  return descriptions[label] ?? label;
}

/** Clarify the group used for historic comparisons without changing its coverage. */
export function historyScope(scope: string): string {
  return scope.replace('punti meteo con dati in tutti i periodi', 'punti di riferimento con dati per tutti gli anni mostrati')
    .replace('comuni con dati in tutti i periodi', 'comuni con dati per tutti gli anni mostrati');
}

/** Keep the original limits of older agricultural censuses in plain language. */
export function historicalDescription(description: string): string {
  return description.replace('con le dimensioni di confronto storico', 'considerate nei censimenti')
    .replace('Montoro non è ricostruito dai comuni precedenti.', 'Per Montoro non sono stati sommati i dati dei comuni precedenti alla fusione.')
    .replace('Montoro non è ricostruito.', 'Per Montoro non sono stati sommati i dati dei comuni precedenti alla fusione.')
    .replace('definizioni e campi di osservazione possono cambiare', 'le definizioni e ciò che viene contato possono cambiare')
    .replace('Le definizioni e i campi di osservazione dei censimenti possono cambiare', 'Le definizioni e ciò che viene contato possono cambiare tra un censimento e l’altro');
}
