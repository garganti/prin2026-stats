#!/usr/bin/env python3
"""Distribuzione dei finanziamenti e confronto delle dimensioni dei progetti PRIN.

Report Markdown e tre CSV nella radice del progetto. L'importo di ogni
progetto viene contato una sola volta dal riepilogo di prin_data.py.
"""
import argparse
import csv
import statistics
import sys
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

from prin_data import PROJECT_ROOT, DATA_DIR, carica_dataset, euro, chiave_ente


def destinazione(percorso):
    p = Path(percorso)
    return p if p.is_absolute() else PROJECT_ROOT / p


def media(importi):
    return sum(importi, Decimal(0)) / Decimal(len(importi)) if importi else Decimal(0)


def mediana(importi):
    return statistics.median(importi) if importi else Decimal(0)


def crea_righe(dati):
    unita_progetto = defaultdict(list)
    for u in dati.unita:
        unita_progetto[(u.settore, u.progetto)].append(u)
    rows = []
    for key, p in dati.progetti.items():
        units = unita_progetto[key]
        if not units:
            raise ValueError(f'Il progetto {key} e senza unita')
        pi = sum(u.ruolo == 'PI' for u in units)
        ru = sum(u.ruolo == 'RU' for u in units)
        if pi != 1:
            raise ValueError(f'Il progetto {key} non ha un unico PI: {pi}')
        enti = set(chiave_ente(u) for u in units)
        mur_pi = sum((u.mur for u in units if u.ruolo == 'PI'), Decimal(0))
        mur_ru = sum((u.mur for u in units if u.ruolo == 'RU'), Decimal(0))
        if mur_pi + mur_ru != p.mur:
            raise ValueError(f'Finanziamento non coerente: {key}')
        rows.append({'settore': p.settore, 'codice': p.codice, 'mur': p.mur,
                     'pi': pi, 'ru': ru, 'unita': len(units), 'enti': len(enti),
                     'mur_pi': mur_pi, 'mur_ru': mur_ru,
                     'mur_per_unita': p.mur / Decimal(len(units))})
    rows.sort(key=lambda r: (r['settore'], -r['mur'], r['codice']))
    return rows


def aggrega_settori(rows):
    grouped = defaultdict(list)
    for r in rows:
        grouped[r['settore']].append(r)
    out = []
    for sector, projects in sorted(grouped.items()):
        amounts = [r['mur'] for r in projects]
        total = sum(amounts, Decimal(0))
        out.append({'settore': sector, 'progetti': len(projects), 'mur_totale': total,
                    'mur_medio': media(amounts), 'mur_mediano': mediana(amounts),
                    'mur_min': min(amounts), 'mur_max': max(amounts),
                    'unita_totali': sum(x['unita'] for x in projects),
                    'unita_medie': Decimal(sum(x['unita'] for x in projects)) / len(projects),
                    'ru_totali': sum(x['ru'] for x in projects),
                    'enti_medi': Decimal(sum(x['enti'] for x in projects)) / len(projects)})
    return out


def aggrega_dimensioni(rows):
    sizes = defaultdict(list)
    for r in rows:
        sizes[r['unita']].append(r)
    return [{'unita': size, 'progetti': len(v),
             'mur_totale': sum((r['mur'] for r in v), Decimal(0)),
             'mur_medio': media([r['mur'] for r in v]),
             'enti_medi': Decimal(sum(r['enti'] for r in v)) / len(v)}
            for size, v in sorted(sizes.items())]


def crea_report(dati, projects, sectors, sizes):
    amounts = [r['mur'] for r in projects]
    total = sum(amounts, Decimal(0))
    n = len(projects)
    assert total == sum((p.mur for p in dati.progetti.values()), Decimal(0))
    units = sum(r['unita'] for r in projects)
    ru = sum(r['ru'] for r in projects)
    lines = [
        '# PRIN 2026 - Analisi economica dei progetti finanziati', '',
        f'**Settori/file:** {len(dati.file)}  ',
        f'**Progetti finanziati:** {n}  ',
        f'**Unita complessive:** {units} (PI: {n}; RU: {ru})  ',
        f'**MUR totale:** {euro(total)} EUR', '',
        '## Statistiche complessive per progetto', '',
        '| Indicatore | Valore |', '|---|---:|',
        f'| Finanziamento medio | {euro(media(amounts))} EUR |',
        f'| Finanziamento mediano | {euro(mediana(amounts))} EUR |',
        f'| Finanziamento minimo | {euro(min(amounts))} EUR |',
        f'| Finanziamento massimo | {euro(max(amounts))} EUR |',
        f'| Unita medie per progetto | {Decimal(units) / n:.2f} |',
        f'| RU medie per progetto | {Decimal(ru) / n:.2f} |', '',
        '## Confronto tra i settori', '',
        '| Settore | Progetti | MUR totale (EUR) | MUR medio | MUR mediano | Min | Max | Unita medie |',
        '|---|---:|---:|---:|---:|---:|---:|---:|',
    ]
    for s in sectors:
        lines.append(f"| {s['settore']} | {s['progetti']} | {euro(s['mur_totale'])} | "
                     f"{euro(s['mur_medio'])} | {euro(s['mur_mediano'])} | "
                     f"{euro(s['mur_min'])} | {euro(s['mur_max'])} | {s['unita_medie']:.2f} |")
    lines.extend(['', '## Dimensioni dei consorzi (numero di unita)', '',
                  '| Unita per progetto | Progetti | Quota progetti | MUR totale (EUR) | MUR medio (EUR) | Enti medi |',
                  '|---:|---:|---:|---:|---:|---:|'])
    for s in sizes:
        lines.append(f"| {s['unita']} | {s['progetti']} | {100 * s['progetti'] / n:.2f}% | "
                     f"{euro(s['mur_totale'])} | {euro(s['mur_medio'])} | {s['enti_medi']:.2f} |")
    lines.extend(['', '## 20 progetti con maggior finanziamento', '',
                  '| Settore | Codice progetto | Unita | Enti | MUR assegnato (EUR) |',
                  '|---|---|---:|---:|---:|'])
    for r in sorted(projects, key=lambda x: (-x['mur'], x['settore'], x['codice']))[:20]:
        lines.append(f"| {r['settore']} | {r['codice']} | {r['unita']} | {r['enti']} | {euro(r['mur'])} |")
    lines.extend(['', '## Note metodologiche', '',
                  '- Il contributo MUR di ciascun progetto e preso dalla tabella riepilogativa, evitando il doppio conteggio delle unita.',
                  '- Per ciascun progetto si controlla che la somma degli importi PI e RU coincida col contributo totale.',
                  '- La dimensione e misurata come **unita PI+RU**; gli enti distinti sono identificati per codice fiscale (se presente).',
                  '- Medie e mediane sono calcolate sui soli progetti **finanziati** inclusi nei file, non su tutte le candidature.',
                  '- Gli output CSV contengono ogni singolo progetto, i riepiloghi di settore e la distribuzione delle dimensioni.', ''])
    if dati.avvisi:
        lines.extend(['## Avvisi relativi ai dati sorgente', ''] + [f'- {a}' for a in dati.avvisi] + [''])
    return '\n'.join(lines)


def write_csv(path, header, rows):
    with path.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(header)
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=DATA_DIR)
    parser.add_argument('--md', type=Path, default=Path('analisi_progetti.md'))
    parser.add_argument('--csv-dir', type=Path, default=Path('.'))
    args = parser.parse_args()
    dati = carica_dataset(destinazione(args.data))
    projects = crea_righe(dati)
    sectors = aggrega_settori(projects)
    sizes = aggrega_dimensioni(projects)
    md = destinazione(args.md)
    csv_dir = destinazione(args.csv_dir)
    md.parent.mkdir(parents=True, exist_ok=True)
    csv_dir.mkdir(parents=True, exist_ok=True)
    md.write_text(crea_report(dati, projects, sectors, sizes), encoding='utf-8')
    p_projects = csv_dir / 'analisi_progetti.csv'
    write_csv(p_projects,
              ['Settore', 'Codice progetto', 'MUR totale EUR', 'PI', 'RU',
               'Unita', 'Enti distinti', 'MUR PI EUR', 'MUR RU EUR', 'MUR medio per unita EUR'],
              ([r['settore'], r['codice'], str(r['mur']), r['pi'], r['ru'],
                r['unita'], r['enti'], str(r['mur_pi']), str(r['mur_ru']),
                str(r['mur_per_unita'])] for r in projects))
    p_sectors = csv_dir / 'analisi_progetti_settori.csv'
    write_csv(p_sectors,
              ['Settore', 'Progetti', 'MUR totale EUR', 'MUR medio EUR', 'MUR mediano EUR',
               'MUR minimo EUR', 'MUR massimo EUR', 'Unita totali', 'Unita medie',
               'RU totali', 'Enti medi per progetto'],
              ([s['settore'], s['progetti'], str(s['mur_totale']), str(s['mur_medio']),
                str(s['mur_mediano']), str(s['mur_min']), str(s['mur_max']),
                s['unita_totali'], str(s['unita_medie']), s['ru_totali'], str(s['enti_medi'])]
               for s in sectors))
    p_sizes = csv_dir / 'analisi_progetti_dimensioni.csv'
    write_csv(p_sizes, ['Unita per progetto', 'Numero progetti', 'MUR totale EUR',
                        'MUR medio EUR', 'Enti medi per progetto'],
              ([s['unita'], s['progetti'], str(s['mur_totale']), str(s['mur_medio']),
                str(s['enti_medi'])] for s in sizes))
    print(f'OK {len(dati.file)} file, {len(projects)} progetti, MUR {euro(sum((r["mur"] for r in projects), Decimal(0)))} EUR')
    print(f'Markdown: {md}\nCSV: {p_projects}\nCSV: {p_sectors}\nCSV: {p_sizes}')
    for avviso in dati.avvisi:
        print(f'AVVISO: {avviso}', file=sys.stderr)


if __name__ == '__main__':
    main()
