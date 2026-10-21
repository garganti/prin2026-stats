# PRIN 2026 - Analisi con output esclusivamente Markdown

La struttura del progetto e':

```text
progetto/
  code/       script Python e documentazione
  data/       23 Excel dei settori e atenei_italiani.csv (anagrafe di input)
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

## Conversioni PDF -> Excel (preparazione dei dati)

I tre convertitori `importa_sh7.py`, `importa_ls6.py` e `importa_hpc_qt.py`
sono strumenti di acquisizione dei dati, non script di analisi: producono
intenzionalmente file `.xlsx` in `data/`. Non modificano la regola sugli output Markdown
degli otto script statistici. Richiedono anche `pdftotext` (Poppler).

## Copertura e controlli

Dataset di riferimento: 23 file Excel, 175 progetti, 196.711.295 EUR MUR.
`prin_data.py` verifica la coerenza tra i finanziamenti delle unita' e dei progetti.
Rimane una incongruenza nel **solo conteggio delle unita' di LS4**, segnalata nei report;
la somma dei finanziamenti risulta coerente. Le statistiche si riferiscono soltanto ai
progetti finanziati dei settori caricati, non a tutte le candidature PRIN.
