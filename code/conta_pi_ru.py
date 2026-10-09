"""Numero di PI e RU distinti per universita/ente; non numero di partecipazioni."""
from collections import defaultdict
from prin_data import PROJECT_ROOT, carica_dataset, chiave_ente, nome_ente

OUTPUT = PROJECT_ROOT / 'conteggio_PI_RU_universita.md'


def main():
    dati = carica_dataset()
    enti = defaultdict(lambda: {'nomi': set(), 'PI': set(), 'RU': set()})
    for u in dati.unita:
        e = enti[chiave_ente(u)]
        e['nomi'].add(u.ente)
        e[u.ruolo].add(u.responsabile.casefold())
    risultati = []
    for e in enti.values():
        pi, ru = len(e['PI']), len(e['RU'])
        risultati.append((nome_ente(e['nomi']), pi, ru, pi + ru))
    risultati.sort(key=lambda r: (-r[3], -r[1], r[0].casefold()))
    tot_pi = sum(r[1] for r in risultati)
    tot_ru = sum(r[2] for r in risultati)
    md = [
        '# Numero di PI e RU per università/ente', '',
        f'File Excel analizzati: **{len(dati.file)}**. Righe PI/RU valide: **{len(dati.unita)}**.', '',
        '| Università / Ente | PI | RU | Totale |',
        '|---|---:|---:|',
    ]
    for ente, pi, ru, totale in risultati:
        md.append(f'| {ente.replace("|", "/")} | {pi} | {ru} | {totale} |')
    md.extend([f'| **TOTALE** | **{tot_pi}** | **{tot_ru}** | **{tot_pi + tot_ru}** |',
               '', 'Nota: i valori contano i **nomi distinti per ente e ruolo**, '
               'non le partecipazioni a progetti. Una persona che svolge entrambi '
               'i ruoli è contata in entrambi. Enti aggregati per codice fiscale.', ''])
    if dati.avvisi:
        md.extend(['## Anomalie nei file sorgente', ''])
        md.extend(f'- {a}' for a in dati.avvisi)
        md.append('')
    OUTPUT.write_text('\n'.join(md), encoding='utf-8')
    print(f'File analizzati: {len(dati.file)}; enti: {len(risultati)}; PI: {tot_pi}; RU: {tot_ru}')
    print(f'Output: {OUTPUT}')
    for avviso in dati.avvisi:
        print(f'AVVISO: {avviso}')


if __name__ == '__main__':
    main()
