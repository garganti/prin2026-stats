# Verifica script PRIN 2026 - Solo Markdown

- Dataset: **23 settori**, **175 progetti**, **196.711.295,00 EUR MUR**.
- Script statistici: **8**, tutti verificati con lettura dei file in `data/`.
- File di output: **8 report Markdown** nella root, uno per script.
- Opzioni di generazione `--csv` e `--csv-dir`: rimosse.
- Dati analitici di dettaglio: inclusi nei Markdown anziche' in CSV.
- Input `data/atenei_italiani.csv`: mantenuto invariato come anagrafe.
- Convertitori `importa_*.py`: continuano a produrre Excel per l'acquisizione di nuovi settori.
- Segnalazione residua: LS4, progetto `2026PKHE87`, riepilogo con 4 unita' e 3 RU a fronte del dettaglio con 5 unita' e 4 RU. Finanziamenti invariati.
