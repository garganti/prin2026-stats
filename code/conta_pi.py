"""Numero di persone PI distinte e progetti con PI per universita/ente."""
from collections import defaultdict
from prin_data import PROJECT_ROOT, carica_dataset, chiave_ente, nome_ente

OUTPUT = PROJECT_ROOT / 'conteggio_PI_per_universita.md'


def main():
    dati = carica_dataset()
    enti = defaultdict(lambda: {'nomi': set(), 'persone': set(), 'progetti': set()})
    for u in dati.unita:
        if u.ruolo != 'PI':
            continue
        e = enti[chiave_ente(u)]
        e['nomi'].add(u.ente)
        e['persone'].add(u.responsabile.casefold())
        e['progetti'].add((u.settore, u.progetto))
    risultati = sorted(
        [(nome_ente(v['nomi']), len(v['persone']), len(v['progetti'])) for v in enti.values()],
        key=lambda x: (-x[1], x[0].casefold()),
    )
    md = [
        '# Numero di persone PI per università/ente', '',
        f'File Excel analizzati: **{len(dati.file)}**.', '',
        '| Università / Ente | Persone PI distinte | Progetti con PI |',
        '|---|---:|---:|',
    ]
    for ente, n_persone, n_progetti in risultati:
        md.append(f'| {ente.replace("|", "/")} | {n_persone} | {n_progetti} |')
    md.extend(['', f'**Totale persone PI (somma per ente): {sum(x[1] for x in risultati)}**',
               '', 'Nota: solo righe con ruolo `PI`; nomi distinti per ente. '
               'Enti aggregati per codice fiscale, quando presente.', ''])
    if dati.avvisi:
        md.extend(['## Anomalie nei file sorgente', ''])
        md.extend(f'- {a}' for a in dati.avvisi)
        md.append('')
    OUTPUT.write_text('\n'.join(md), encoding='utf-8')
    print(f'File analizzati: {len(dati.file)}; enti: {len(risultati)}; output: {OUTPUT}')
    for avviso in dati.avvisi:
        print(f'AVVISO: {avviso}')


if __name__ == '__main__':
    main()
