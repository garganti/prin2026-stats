# Script PRIN 2026: istruzioni

I file `.py` devono rimanere in `code/` e gli Excel da elaborare in una directory sorella `data/`.

```text
progetto/
  code/
    prin_data.py
    conta_pi.py
    conta_pi_ru.py
    riepilogo_settori.py
    finanziamenti_per_ateneo.py
  data/
    *.xlsx
  conteggio_PI_per_universita.md
  conteggio_PI_RU_universita.md
  riepilogo_settori.md
  riepilogo_finanziamenti_atenei.md
```

Installa la dipendenza con `python -m pip install openpyxl`.

Esegui dalla cartella `progetto/`:

```bash
python code/conta_pi.py
python code/conta_pi_ru.py
python code/riepilogo_settori.py
python code/finanziamenti_per_ateneo.py
```

I quattro report Markdown sono salvati nella directory principale `progetto/`, anche se gli script vengono lanciati da un altro percorso: `PROJECT_ROOT` viene calcolato a partire da `code/prin_data.py`, non dalla directory di lavoro. Anche il percorso `--md risultato.md` e' relativo a `progetto/`; con `--md /percorso/assoluto/risultato.md` si puo' invece scegliere un'altra destinazione. I file Python rimangono in `code/`. Per esportare i finanziamenti anche in CSV:

```bash
python code/finanziamenti_per_ateneo.py --csv riepilogo.csv
```

Per usare una diversa cartella Excel con lo script dei finanziamenti:

```bash
python code/finanziamenti_per_ateneo.py /percorso/agli/xlsx --md risultato.md
```

Il modulo `prin_data.py` riconosce sia i file con unità nel foglio `Progetti` sia quelli con il foglio `Unita`. Verifica che la somma MUR delle unità corrisponda all'importo dei progetti; eventuali discrepanze bloccano l'elaborazione. Discrepanze nei soli conteggi dichiarati delle unità e codici unità duplicati vengono segnalati, senza eliminare le righe. Rimane un'anomalia di conteggio nel file LS4, descritta in `verifica_esecuzione.md`. La duplicazione del codice unità PE1 è stata corretta.
