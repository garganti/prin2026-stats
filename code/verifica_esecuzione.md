# Verifica degli script Python sui file PRIN

Esito: **4/4 script eseguiti con successo** e **19/19 file Excel letti e validati**.

- Progetti: **155**
- Unità di ricerca: **787** (**155 PI** e **632 RU**)
- Totale MUR: **171.593.427,00 €**
- Atenei/enti nei risultati finanziari: **90**

I totali MUR nei fogli di riepilogo coincidono con la somma delle unità per tutti i 155 progetti. Il file PE1 è stato corretto su richiesta: il codice unità di MARTINAZZI Luca Massimo Andrea è passato da `2026P3T2LW_004` a `2026P3T2LW_005`. I dati finanziari non sono stati modificati.

## Controlli per file

| File Excel | Progetti | Unità | Anomalie segnalate |
|---|---:|---:|---:|
| CYB_Tabella_B_Progetti_finanziati.xlsx | 4 | 20 | 0 |
| IA_Tabella_B_Progetti_finanziati.xlsx | 13 | 72 | 0 |
| LS2_Tabella_B_Progetti_finanziati.xlsx | 5 | 21 | 0 |
| LS3_Tabella_B_Progetti_finanziati.xlsx | 4 | 18 | 0 |
| LS4_Tabella_B_Progetti_finanziati.xlsx | 12 | 65 | 2 |
| LS7_Tabella_B_Progetti_finanziati.xlsx | 17 | 87 | 0 |
| PE10_Tabella_B_Progetti_finanziati.xlsx | 9 | 41 | 0 |
| PE11_Tabella_B_Progetti_finanziati.xlsx | 6 | 32 | 0 |
| PE1_Tabella_B_Progetti_finanziati.xlsx | 5 | 28 | 0 |
| PE2_Tabella_B_Progetti_finanziati.xlsx | 6 | 28 | 0 |
| PE3_Tabella_B_Progetti_finanziati.xlsx | 5 | 25 | 0 |
| PE5_Tabella_B_Progetti_finanziati.xlsx | 8 | 43 | 0 |
| PE6_Tabella_B_Progetti_finanziati.xlsx | 6 | 31 | 0 |
| PE7_Tabella_B_Progetti_finanziati.xlsx | 11 | 57 | 0 |
| PE8_Tabella_B_Progetti_finanziati.xlsx | 14 | 75 | 0 |
| PE9_Tabella_B_Progetti_finanziati.xlsx | 4 | 19 | 0 |
| SH4_Tabella_B_Progetti_finanziati.xlsx | 8 | 36 | 0 |
| SH5_Tabella_B_Progetti_finanziati.xlsx | 9 | 47 | 0 |
| SH6_Tabella_B_Progetti_finanziati.xlsx | 9 | 42 | 0 |

## Anomalie dei dati di origine

- LS4_Tabella_B_Progetti_finanziati.xlsx: 2026PKHE87: nel riepilogo N. unità=4, ma righe di dettaglio=5
- LS4_Tabella_B_Progetti_finanziati.xlsx: 2026PKHE87: nel riepilogo N. RU=3, ma righe RU di dettaglio=4

Le incongruenze sul numero di unità e sui codici unità non alterano i totali MUR, verificati sui fogli riepilogativi.

## Controlli di esecuzione

- Compilazione Python: superata.
- Esecuzione dei quattro script dalla directory `/tmp`: superata.
- Elaborazione di ciascuno dei 19 file separatamente: superata.
- Esecuzione su tutti i file insieme: superata.
- Esportazione CSV con somma degli importi verificata: superata.
- Directory dati vuota: errore esplicito (anziché produrre risultati falsamente vuoti).
- Integrità degli altri 18 file Excel: nessuna modifica; aggiornato soltanto il codice unità PE1 richiesto.
- Verifica successiva alla correzione: esecuzione dei quattro script superata senza duplicazioni PE1.

## Posizione degli output (aggiornamento)

I quattro script salvano i report Markdown in `/mnt/data/`, mentre i file sorgente Excel vengono letti da `/mnt/data/data/`. Il percorso di output viene derivato dalla posizione dello script e non dalla directory di esecuzione.
