# Verifica PRIN 2026 - 30 settori

- Nuovi PDF acquisiti: HT, SH3, SH8, LS8, PE4, LS9, LS5.
- I sette PDF sono stati convertiti in fogli Excel `Riepilogo` e `Progetti`.
- Verifica per ogni progetto: somma dei MUR delle unità = totale progetto nel PDF.
- Verifica per ciascun settore: somma dei progetti = totale complessivo riportato nel PDF.
- I sette nuovi settori comprendono 64 progetti, 311 unità (64 PI, 247 RU), 74.413.494 EUR MUR.
- Dataset completo: 30 settori, 239 progetti, 1.201 unità (239 PI, 962 RU), 271.124.789 EUR MUR.
- Tutti gli otto script statistici sono stati eseguiti dalla cartella `/tmp`: esito positivo.
- I report statistici vengono generati solo in Markdown, nella root del progetto.
- Anagrafe CF aggiornata per Bocconi, UnitelmaSapienza e UNINETTUNO sulla base dei nuovi PDF; 89 atenei con partecipazioni, 12 senza su 101 censiti.

## Anomalie dei dati sorgente ancora presenti

- LS4, progetto `2026PKHE87`: il riepilogo conta 4 unità, il dettaglio ne contiene 5.
- LS4, stesso progetto: il riepilogo conta 3 RU, il dettaglio ne contiene 4.
- Entrambe le incongruenze sono segnalate nei report. I finanziamenti coincidono.

## Ambito

Le tabelle di tutti i settori contengono i soli progetti finanziati. L'assenza di partecipazioni per un ateneo non consente di concludere che non abbia presentato proposte, né descrive eventuali settori non presenti nei file.

Le marcature dei PI under 40 nei sette nuovi file Excel sono state lasciate **non verificate**; nessuna inferenza sull'età dei PI è stata effettuata.
