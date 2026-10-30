# PRIN 2026 - Analisi con output esclusivamente Markdown

La struttura del progetto e':

```text
progetto/
  code/       script Python e documentazione
  data/       30 Excel dei settori e atenei_italiani.csv (anagrafe di input)
  *.md        report statistici generati nella root
```

## Dipendenze

Per gli script di analisi e' sufficiente Python 3 con `openpyxl`:

```bash
python -m pip install openpyxl
```

## Gli otto script di analisi

| Comando | Unico file di output |
|---|---|
| `python code/conta_pi.py` | `conteggio_PI_per_universita.md` |
| `python code/conta_pi_ru.py` | `conteggio_PI_RU_universita.md` |
| `python code/finanziamenti_per_ateneo.py` | `riepilogo_finanziamenti_atenei.md` |
| `python code/riepilogo_settori.py` | `riepilogo_settori.md` |
| `python code/analisi_leadership.py` | `analisi_leadership.md` |
| `python code/rete_collaborazioni.py` | `rete_collaborazioni.md` |
| `python code/analisi_progetti.py` | `analisi_progetti.md` |
| `python code/atenei_senza_progetti.py` | `atenei_senza_progetti.md` |

Tutti i report sono scritti nella **root del progetto**, individuata dalla posizione degli script,
non dalla directory di lavoro corrente. Gli script non producono CSV, XLSX, PDF, immagini o
altri file di risultato. Le normali informazioni diagnostiche sono stampate nel terminale.

Per gli script che supportano le opzioni `--data` e `--md`, i percorsi relativi sono riferiti
alla root del progetto; `--md report/analisi.md` crea una sottocartella nel progetto.
L'opzione `--csv` e l'opzione `--csv-dir` sono state rimosse.

Le tabelle complete precedentemente esportate in CSV sono ora comprese nel Markdown:
- `analisi_leadership.md`: enti, persone distinte, ruoli, settori, progetti, finanziamenti, Gini e HHI.
- `rete_collaborazioni.md`: indici per tutti i nodi e tutti gli archi, compresi i progetti condivisi.
- `analisi_progetti.md`: tutti i progetti, importi PI e RU, analisi per settore e dimensioni dei consorzi.
- `atenei_senza_progetti.md`: assenti, distribuzioni, soli RU e tabella di tutti gli atenei censiti.
- `riepilogo_finanziamenti_atenei.md`: anche il codice fiscale degli enti.

**Attenzione:** `data/atenei_italiani.csv` e' un *file sorgente* necessario per
`atenei_senza_progetti.py`. Rimane in formato CSV per preservare l'anagrafe preesistente:
non e' un output degli script.

## Eseguire tutte le analisi insieme

Dalla root del progetto, eseguire:

```bash
python run_all.py
```

Il comando trova e lancia in ordine alfabetico tutti gli script statistici `*.py`
nella cartella `code/`, mantenendo i report Markdown nella root. I convertitori
`importa_*.py` e il modulo di supporto `prin_data.py` sono esclusi per evitare
di sovrascrivere i file Excel originali.

Altre opzioni:

```bash
python run_all.py --list           # mostra i programmi selezionati
python run_all.py --stop-on-error  # interrompe al primo errore
python run_all.py --all            # esegue letteralmente ogni file .py in code/
```

Attenzione: `--all` esegue anche i convertitori PDF->Excel e potrebbe riscrivere
file in `data/`; usarlo solo quando si desidera importare nuovamente i PDF.
Il programma restituisce codice di uscita 1 quando almeno uno script fallisce.

## Conversioni PDF -> Excel (preparazione dei dati)

I quattro convertitori `importa_sh7.py`, `importa_ls6.py`, `importa_hpc_qt.py` e `importa_nuovi_settori.py`
sono strumenti di acquisizione dei dati, non script di analisi: producono
intenzionalmente file `.xlsx` in `data/`. Non modificano la regola sugli output Markdown
degli otto script statistici. Richiedono anche `pdftotext` (Poppler).

## Copertura e controlli

Dataset aggiornato: 30 file Excel, 239 progetti, 962 RU, 271.124.789 EUR MUR.
`prin_data.py` verifica la coerenza tra i finanziamenti delle unita' e dei progetti.
Rimane una incongruenza nel **solo conteggio delle unita' di LS4**, segnalata nei report;
la somma dei finanziamenti risulta coerente. Le statistiche si riferiscono soltanto ai
progetti finanziati dei settori caricati, non a tutte le candidature PRIN.

## Nuovi settori (29 ottobre 2026)

Sono stati importati i PDF **HT, SH3, SH8, LS8, PE4, LS9 e LS5**, con
64 progetti, 311 unita e 74.413.494 EUR MUR.

I PDF originali devono trovarsi nella root oppure nella sottocartella `fonti/` per rigenerare gli Excel:

```bash
python code/importa_nuovi_settori.py
```

L'importatore valida i contributi delle singole unita, i subtotali di progetto e
i totali di settore. Nel file PE4 il PDF originale e' denominato
`PE4_Tabella_B_Graduatoria finale.pdf`, pur riportando in intestazione la Tabella B
dei progetti finanziati.

Le descrizioni degli enti spezzate sulle righe dei PDF sono state ricostruite usando
le denominazioni degli enti gia' presenti nel dataset e il codice fiscale; per gli
enti nuovi e' stata usata la denominazione del PDF. I dati PI under 40 dei sette
settori non sono stati ricostruiti e sono indicati come **non verificati**.

L'anagrafe degli atenei e' stata aggiornata con i CF di Bocconi,
UnitelmaSapienza e UNINETTUNO, ricavati dai PDF, per impedire falsi assenti.
Nel dataset attuale sono censiti 101 atenei, 89 con e 12 senza partecipazioni.
