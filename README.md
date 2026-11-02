# IrpiniaConta

IrpiniaConta è un progetto indipendente che racconta attraverso i dati i 118 comuni della provincia di Avellino. Nasce dal desiderio di rendere più facile conoscere il territorio: persone, imprese, ambiente, servizi e cambiamenti nel tempo.

Il sito riunisce dati provenienti da fonti diverse e li presenta con mappe e grafici. È possibile esplorare l’Irpinia, aprire la pagina di un comune e confrontare più territori. Ogni indicatore conserva il periodo e la fonte; un dato mancante non viene trattato come zero.

Il progetto è amatoriale e non istituzionale. Le elaborazioni possono contenere errori, omissioni o dati non aggiornati: per usi ufficiali è necessario consultare le fonti originali.

## Come funziona

L’interfaccia e le API sono realizzate con Nuxt, Vue e TypeScript. PostgreSQL ospita i dati pubblicati; una pipeline Python acquisisce, verifica e prepara i dati dalle fonti. Le pagine mostrano le fonti e il periodo di riferimento dei singoli indicatori.

Il progetto è di [Francesco Bianco](https://francescobianco.it). Il codice è pubblicato per documentare il lavoro e favorire la trasparenza; non è attualmente organizzato come progetto a contribuzione aperta.

## Codice e dati

La repository contiene il codice e la configurazione delle fonti. Database, acquisizioni originali, stemmi, credenziali e pubblicazioni dei dati sono gestiti separatamente: il solo codice non contiene i dati necessari per riprodurre il sito popolato. Per le procedure locali e il trasferimento dei dati, vedi [data/README.md](data/README.md).

Le fonti e le rispettive condizioni sono indicate nel catalogo del sito e in `config/sources.json`. Ogni fonte può prevedere obblighi di attribuzione o altre condizioni proprie.

## Licenza e riconoscimenti

Il codice è distribuito con [licenza MIT](LICENSE). La licenza del codice non modifica le condizioni applicabili a dati, font, stemmi e altri contenuti di terzi. Il font Manrope incluso è distribuito secondo la SIL Open Font License: vedi [app/assets/fonts/README.md](app/assets/fonts/README.md).
