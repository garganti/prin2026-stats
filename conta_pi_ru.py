"""Conta PI e RU distinti per universita/ente in tutti gli Excel di data/."""
from collections import defaultdict
from pathlib import Path
import openpyxl

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
OUTPUT = BASE_DIR / 'conteggio_PI_RU_universita.md'

# Il codice fiscale permette di unire nomi diversi dello stesso ateneo.
enti = defaultdict(lambda: {'nomi': set(), 'PI': set(), 'RU': set()})
file_letti = 0
righe_valide = 0

for file in sorted(DATA_DIR.glob('*.xlsx')):
    if file.name.startswith('~$'):
        continue
    wb = openpyxl.load_workbook(file, read_only=True, data_only=True)
    try:
        if 'Progetti' not in wb.sheetnames:
            print(f'Salto {file.name}: foglio Progetti assente')
            continue
        righe = iter(wb['Progetti'].values)
        intestazioni = None
        for riga in righe:
            candidate = [str(v).strip().casefold() if v is not None else '' for v in riga]
            if 'ruolo' in candidate and 'ateneo/ente' in candidate:
                intestazioni = candidate
                break
        if intestazioni is None:
            print(f'Salto {file.name}: intestazioni non trovate')
            continue

        idx_ruolo = intestazioni.index('ruolo')
        idx_ente = intestazioni.index('ateneo/ente')
        idx_persona = next((i for i, v in enumerate(intestazioni)
                            if 'responsabile unit' in v), None)
        idx_cf = next((i for i, v in enumerate(intestazioni)
                       if 'codice fiscale' in v), None)
        if idx_persona is None:
            print(f'Salto {file.name}: colonna responsabile assente')
            continue

        for riga in righe:
            ruolo = str(riga[idx_ruolo] or '').strip().upper()
            if ruolo not in ('PI', 'RU'):
                continue
            ente = str(riga[idx_ente] or '').strip()
            persona = str(riga[idx_persona] or '').strip()
            cf = str(riga[idx_cf] or '').strip() if idx_cf is not None else ''
            if not ente or not persona:
                continue
            chiave = cf if cf else ente.casefold()
            enti[chiave]['nomi'].add(ente)
            enti[chiave][ruolo].add(' '.join(persona.casefold().split()))
            righe_valide += 1
        file_letti += 1
    finally:
        wb.close()

risultati = []
for dati in enti.values():
    nome = sorted(dati['nomi'], key=lambda n: (len(n), n))[0]
    pi, ru = len(dati['PI']), len(dati['RU'])
    risultati.append((nome, pi, ru, pi + ru))
risultati.sort(key=lambda r: (-r[3], -r[1], r[0].casefold()))

tot_pi = sum(r[1] for r in risultati)
tot_ru = sum(r[2] for r in risultati)
md = [
    '# Numero di PI e RU per università/ente',
    '',
    f'File Excel analizzati: **{file_letti}**. Righe PI/RU valide: **{righe_valide}**.',
    '',
    '| Università / Ente | PI | RU | Totale |',
    '|---|---:|---:|---:|',
]
for ente, pi, ru, totale in risultati:
    md.append(f'| {ente.replace("|", "/")} | {pi} | {ru} | {totale} |')
md += [
    f'| **TOTALE** | **{tot_pi}** | **{tot_ru}** | **{tot_pi + tot_ru}** |',
    '',
    'Nota: i valori PI e RU contano i **nomi distinti per ente e ruolo**, '
    'non le partecipazioni a progetti. La stessa persona presente in entrambi '
    'i ruoli viene contata una volta in ciascuna colonna. '
    'Gli enti con lo stesso codice fiscale sono aggregati.',
    '',
]
OUTPUT.write_text('\n'.join(md), encoding='utf-8')
print(f'File analizzati: {file_letti}; enti: {len(risultati)}; PI: {tot_pi}; RU: {tot_ru}')
print(f'Risultato salvato in {OUTPUT}')
