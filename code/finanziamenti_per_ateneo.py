#!/usr/bin/env python3
"""Finanziamenti PRIN per ateneo/ente e percentuale sul totale.

Esempi:
  python code/finanziamenti_per_ateneo.py
  python code/finanziamenti_per_ateneo.py data --md riepilogo_atenei.md --csv riepilogo.csv
Dipendenza: pip install openpyxl
"""
import argparse
import csv
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

from prin_data import PROJECT_ROOT, DATA_DIR, carica_dataset, chiave_ente, euro, nome_ente

OUTPUT = PROJECT_ROOT / 'riepilogo_finanziamenti_atenei.md'


def calcola(cartella=DATA_DIR):
    dati = carica_dataset(cartella)
    importi = defaultdict(lambda: Decimal(0))
    nomi = defaultdict(set)
    for u in dati.unita:
        key = chiave_ente(u)
        importi[key] += u.mur
        nomi[key].add(u.ente)
    totale = sum(importi.values(), Decimal(0))
    risultati = sorted(
        ((nome_ente(nomi[k]), k[1] if k[0] == 'cf' else '', s,
          s / totale * 100 if totale else Decimal(0)) for k, s in importi.items()),
        key=lambda r: (-r[2], r[0].casefold()),
    )
    return risultati, totale, dati


def crea_markdown(risultati, totale, nfile, avvisi=()):
    righe = [
        '# Finanziamenti PRIN 2026 per università/ente', '',
        f'**File Excel analizzati:** {nfile}  ',
        f'**Enti distinti:** {len(risultati)}  ',
        f'**Finanziamento MUR complessivo:** {euro(totale)} €', '',
        '| Pos. | Università / Ente | Totale finanziato (EUR) | % sul totale |',
        '|---:|---|---:|---:|',
    ]
    for pos, (nome, _, somma, quota) in enumerate(risultati, 1):
        nome_md = nome.replace('|', '\\|').replace('\n', ' ').replace('\r', ' ')
        percentuale = f'{quota:.2f}'.replace('.', ',')
        righe.append(f'| {pos} | {nome_md} | {euro(somma)} € | {percentuale}% |')
    righe.append(f'| | **TOTALE** | **{euro(totale)} €** | **100,00%** |')
    righe.extend(['', '*Percentuale rispetto alla somma dei contributi MUR assegnati '
                  'alle unità di ricerca dei file analizzati.*', ''])
    if avvisi:
        righe.extend(['## Anomalie riscontrate nei file sorgente', ''])
        righe.extend(f'- {a}' for a in avvisi)
        righe.append('')
    return '\n'.join(righe)


def main():
    parser = argparse.ArgumentParser(description='Finanziamenti MUR e percentuale per ateneo/ente')
    parser.add_argument('cartella', nargs='?', type=Path, default=DATA_DIR,
                        help=f'Cartella XLSX (predefinita: {DATA_DIR})')
    parser.add_argument('--md', type=Path, default=OUTPUT, help=f'Output Markdown (predefinito: {OUTPUT})')
    parser.add_argument('--csv', type=Path, help='Output CSV opzionale')
    args = parser.parse_args()
    try:
        risultati, totale, dati = calcola(args.cartella)
    except (ValueError, FileNotFoundError, KeyError) as exc:
        parser.error(str(exc))
    markdown = crea_markdown(risultati, totale, len(dati.file), dati.avvisi)
    print(markdown, end='')
    percorso_md = args.md if args.md.is_absolute() else PROJECT_ROOT / args.md
    percorso_md.write_text(markdown, encoding='utf-8')
    print(f'\nFile Markdown scritto in: {percorso_md}', file=sys.stderr)
    for avviso in dati.avvisi:
        print(f'AVVISO: {avviso}', file=sys.stderr)
    if args.csv:
        with args.csv.open('w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['Ateneo/Ente', 'Codice fiscale', 'Totale MUR assegnato (€)', 'Percentuale (%)'])
            for nome, cf, somma, quota in risultati:
                writer.writerow([nome, cf, str(somma), f'{quota:.4f}'])
        print(f'CSV scritto in: {args.csv}', file=sys.stderr)


if __name__ == '__main__':
    main()
