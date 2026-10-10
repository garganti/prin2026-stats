#!/usr/bin/env python3
"""Leadership, diversificazione e concentrazione PRIN 2026.

Dipendenza: openpyxl e modulo locale prin_data.py.
Lettura: <radice>/data/*.xlsx; output MD/CSV: <radice>/.
L'aggregazione degli enti usa il codice fiscale, se disponibile.
"""
import argparse
import csv
import sys
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

from prin_data import PROJECT_ROOT, DATA_DIR, carica_dataset, chiave_ente, euro, nome_ente


def destinazione(percorso):
    p = Path(percorso)
    return p if p.is_absolute() else PROJECT_ROOT / p


def percentuale(parte, totale):
    return 100 * parte / totale if totale else Decimal(0)


def gini(importi):
    """Gini, [0,1], calcolato sugli importi ricevuti dai soli enti presenti."""
    v = sorted(importi)
    n = len(v)
    s = sum(v, Decimal(0))
    if not n or not s:
        return Decimal(0)
    return (Decimal(2) * sum((Decimal(i) * x for i, x in enumerate(v, 1)), Decimal(0)) /
            (Decimal(n) * s) - Decimal(n + 1) / Decimal(n))


def hhi(importi):
    """Herfindahl-Hirschman Index (0..10000), con quote percentuali al quadrato."""
    s = sum(importi, Decimal(0))
    return sum(((100 * x / s) ** 2 for x in importi), Decimal(0)) if s else Decimal(0)


def testo_md(s):
    return str(s).replace('|', '\\|').replace('\n', ' ')


def analizza(dati):
    enti = defaultdict(lambda: {
        'nomi': set(), 'PI': 0, 'RU': 0, 'persone_pi': set(), 'persone_ru': set(),
        'mur_pi': Decimal(0), 'mur_ru': Decimal(0), 'progetti': set(), 'settori': set(),
    })
    for u in dati.unita:
        key = chiave_ente(u)
        r = enti[key]
        r['nomi'].add(u.ente)
        r[u.ruolo] += 1
        r['persone_pi' if u.ruolo == 'PI' else 'persone_ru'].add(u.responsabile.casefold())
        r['mur_pi' if u.ruolo == 'PI' else 'mur_ru'] += u.mur
        r['progetti'].add((u.settore, u.progetto))
        r['settori'].add(u.settore)

    rows = []
    for key, r in enti.items():
        totale_mur = r['mur_pi'] + r['mur_ru']
        rows.append({
            'ente': nome_ente(r['nomi']), 'codice_fiscale': key[1] if key[0] == 'cf' else '',
            'pi': r['PI'], 'ru': r['RU'], 'persone_pi': len(r['persone_pi']),
            'persone_ru': len(r['persone_ru']), 'partecipazioni': r['PI'] + r['RU'],
            'progetti': len(r['progetti']), 'mur_pi': r['mur_pi'], 'mur_ru': r['mur_ru'],
            'mur_totale': totale_mur, 'settori': sorted(r['settori']),
            'num_settori': len(r['settori']),
            'rapporto_pi_ru': Decimal(r['PI']) / r['RU'] if r['RU'] else None,
        })
    rows.sort(key=lambda r: (-r['mur_totale'], -r['pi'], r['ente'].casefold()))
    totale = sum((p.mur for p in dati.progetti.values()), Decimal(0))
    assert sum((r['mur_totale'] for r in rows), Decimal(0)) == totale, 'MUR non coerente'
    return rows, totale


def tabella(rows, totale):
    r = ['| Ateneo / Ente | PI | RU | PI/RU | Settori | MUR PI | MUR RU | MUR totale | Quota |',
         '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for e in rows:
        q = percentuale(e['mur_totale'], totale)
        ratio = f"{e['rapporto_pi_ru']:.2f}" if e['rapporto_pi_ru'] is not None else 'n.d.'
        r.append(f"| {testo_md(e['ente'])} | {e['pi']} | {e['ru']} | {ratio} | "
                 f"{e['num_settori']} | {euro(e['mur_pi'])} | {euro(e['mur_ru'])} | "
                 f"{euro(e['mur_totale'])} | {q:.2f}% |")
    return r


def crea_report(dati, rows, totale):
    pi_tot = sum(r['pi'] for r in rows)
    ru_tot = sum(r['ru'] for r in rows)
    importi = [r['mur_totale'] for r in rows]
    top5 = sum(importi[:5], Decimal(0))
    top10 = sum(importi[:10], Decimal(0))
    lines = [
        '# PRIN 2026 - Leadership e finanziamenti degli atenei', '',
        f'**Settori/file:** {len(dati.file)}  ',
        f'**Progetti:** {len(dati.progetti)}  ',
        f'**Atenei/enti distinti:** {len(rows)}  ',
        f'**Partecipazioni PI:** {pi_tot}  ',
        f'**Partecipazioni RU:** {ru_tot}  ',
        f'**MUR totale:** {euro(totale)} EUR', '',
        '## Distribuzione dei ruoli e del finanziamento', '',
        f'- Finanziamento assegnato a unità PI: **{euro(sum((x["mur_pi"] for x in rows), Decimal(0)))} EUR**.',
        f'- Finanziamento assegnato a unità RU: **{euro(sum((x["mur_ru"] for x in rows), Decimal(0)))} EUR**.',
        f'- Quota finanziamenti primi 5 enti: **{percentuale(top5, totale):.2f}%**.',
        f'- Quota finanziamenti primi 10 enti: **{percentuale(top10, totale):.2f}%**.',
        f'- Indice di Gini degli importi per ente: **{gini(importi):.4f}**.',
        f'- HHI degli importi per ente (scala 0-10000): **{hhi(importi):.1f}**.', '',
        '## Classifica finanziamenti per ateneo / ente', '',
    ]
    lines.extend(tabella(rows, totale))
    diversificati = sorted(rows, key=lambda r: (-r['num_settori'], -r['progetti'], r['ente'].casefold()))
    leader = sorted(rows, key=lambda r: (-r['pi'], -r['ru'], r['ente'].casefold()))
    lines.extend(['', '## I 20 atenei con piu progetti coordinati (PI)', '',
                  '| Ateneo / Ente | Progetti coordinati (PI) | Partecipazioni RU | Progetti distinti |',
                  '|---|---:|---:|---:|'])
    for r in leader[:20]:
        lines.append(f"| {testo_md(r['ente'])} | {r['pi']} | {r['ru']} | {r['progetti']} |")
    lines.extend(['', '## Diversificazione scientifica: 20 enti con piu settori', '',
                  '| Ateneo / Ente | Settori | Progetti distinti | Codici settori |',
                  '|---|---:|---:|---|'])
    for r in diversificati[:20]:
        lines.append(f"| {testo_md(r['ente'])} | {r['num_settori']} | {r['progetti']} | "
                     f"{', '.join(r['settori'])} |")
    lines.extend(['', '## Metodo', '',
                  '- Il ruolo PI/RU conta **partecipazioni di unita** (non persone distinte); le persone distinte sono nel CSV.',
                  '- PI/RU = partecipazioni PI divise per le partecipazioni RU; se RU = 0, il rapporto non e definito.',
                  '- Un progetto e contato una sola volta per ente, anche in presenza di piu unita dello stesso ente.',
                  '- I codici fiscali sono usati per identificare gli enti quando presenti.',
                  '- Gini e HHI descrivono la concentrazione dei finanziamenti **fra gli enti presenti nei file**.',
                  '- Questi dati riguardano esclusivamente progetti finanziati; non misurano i tassi di successo delle candidature.', ''])
    if dati.avvisi:
        lines.extend(['## Avvisi relativi ai dati sorgente', ''] + [f'- {testo_md(x)}' for x in dati.avvisi] + [''])
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=DATA_DIR, help='Cartella dei file xlsx')
    parser.add_argument('--md', type=Path, default=Path('analisi_leadership.md'), help='Report Markdown')
    parser.add_argument('--csv-dir', type=Path, default=Path('.'), help='Cartella per i CSV')
    args = parser.parse_args()
    dati = carica_dataset(destinazione(args.data))
    rows, totale = analizza(dati)
    md = destinazione(args.md)
    outdir = destinazione(args.csv_dir)
    md.parent.mkdir(parents=True, exist_ok=True)
    outdir.mkdir(parents=True, exist_ok=True)
    md.write_text(crea_report(dati, rows, totale), encoding='utf-8')
    csv_path = outdir / 'analisi_leadership.csv'
    with csv_path.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Ente', 'Codice fiscale', 'PI partecipazioni', 'RU partecipazioni',
                         'PI persone distinte', 'RU persone distinte', 'Progetti distinti',
                         'Settori distinti', 'Elenco settori', 'MUR PI EUR', 'MUR RU EUR',
                         'MUR totale EUR', 'Quota totale pct', 'Rapporto PI/RU'])
        for r in rows:
            writer.writerow([r['ente'], r['codice_fiscale'], r['pi'], r['ru'],
                             r['persone_pi'], r['persone_ru'], r['progetti'], r['num_settori'],
                             '|'.join(r['settori']), str(r['mur_pi']), str(r['mur_ru']),
                             str(r['mur_totale']), f"{percentuale(r['mur_totale'], totale):.4f}",
                             '' if r['rapporto_pi_ru'] is None else f"{r['rapporto_pi_ru']:.4f}"])
    print(f'OK {len(dati.file)} file, {len(dati.progetti)} progetti, {len(rows)} enti; MUR {euro(totale)} EUR')
    print(f'Markdown: {md}\nCSV: {csv_path}')
    for avviso in dati.avvisi:
        print(f'AVVISO: {avviso}', file=sys.stderr)


if __name__ == '__main__':
    main()
