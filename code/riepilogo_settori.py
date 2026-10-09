"""Progetti, unita con ruolo RU e contributo MUR totale per settore."""
from collections import Counter, defaultdict
from decimal import Decimal
from prin_data import PROJECT_ROOT, carica_dataset, euro

OUTPUT = PROJECT_ROOT / 'riepilogo_settori.md'


def main():
    dati = carica_dataset()
    progetti = Counter(p.settore for p in dati.progetti.values())
    ru = Counter(u.settore for u in dati.unita if u.ruolo == 'RU')
    importi = defaultdict(lambda: Decimal(0))
    for progetto in dati.progetti.values():
        importi[progetto.settore] += progetto.mur
    righe = ['# Riepilogo progetti finanziati per settore', '',
             f'File Excel analizzati: **{len(dati.file)}**.', '',
             '| Settore | Progetti | RU | Contributo MUR totale (€) |',
             '|:---|---:|---:|---:|']
    for settore in sorted(progetti):
        righe.append(f'| {settore} | {progetti[settore]} | {ru[settore]} | {euro(importi[settore])} |')
    righe.append(f'| **TOTALE** | **{sum(progetti.values())}** | **{sum(ru.values())}** | '
                 f'**{euro(sum(importi.values(), Decimal(0)))}** |')
    righe.extend(['', 'RU = unità di ricerca con ruolo RU (esclusi i PI). '
                  'Gli importi sono sommati una sola volta per progetto.', ''])
    if dati.avvisi:
        righe.extend(['## Anomalie nei file sorgente', ''])
        righe.extend(f'- {a}' for a in dati.avvisi)
        righe.append('')
    OUTPUT.write_text('\n'.join(righe), encoding='utf-8')
    print('\n'.join(righe))
    print(f'\nSalvato: {OUTPUT}')
    for avviso in dati.avvisi:
        print(f'AVVISO: {avviso}')


if __name__ == '__main__':
    main()
