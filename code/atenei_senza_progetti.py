#!/usr/bin/env python3
"""Atenei italiani assenti (PI e RU) dalle tabelle PRIN finanziate.

Confronta la lista degli atenei italiani in <progetto>/data/atenei_italiani.csv
con tutti i file <progetto>/data/*.xlsx usando i codici fiscali dove noti.
I nomi vengono confrontati esattamente dopo normalizzazione solo se manca
il codice fiscale: NON usa fuzzy matching, per evitare falsi positivi.

Output predefiniti nella root del progetto:
    atenei_senza_progetti.md
    atenei_senza_progetti.csv
    partecipazione_atenei_italiani.csv

Attenzione: assenza nei file analizzati NON significa assenza di finanziamenti
in altri settori/bandi, ne' indica una candidatura respinta.
"""
import argparse
import csv
import sys
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

from prin_data import DATA_DIR, PROJECT_ROOT, carica_dataset, chiave_ente, euro, normalizza

URL_USTAT = 'https://ustat.mur.gov.it/dati/didattica/italia/atenei'
URL_MUR = 'https://www.mur.gov.it/en/node/2166'


def destinazione(path):
    path = Path(path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def leggi_anagrafe(path):
    if not path.is_file():
        raise FileNotFoundError(
            f'Anagrafe non trovata: {path}. ' 
            'Fornire un CSV con colonne nome, regione, tipo, codice_fiscale, fonte.')
    with path.open(newline='', encoding='utf-8-sig') as stream:
        reader = csv.DictReader(stream, delimiter=';')
        obbligatori = {'nome', 'regione', 'tipo', 'codice_fiscale', 'fonte'}
        if not reader.fieldnames or not obbligatori <= set(reader.fieldnames):
            raise ValueError(f'Colonne mancanti in {path}: {obbligatori - set(reader.fieldnames or [])}')
        atenei = [{k: (v or '').strip() for k, v in r.items()} for r in reader]
    if not atenei:
        raise ValueError('Anagrafe vuota')
    cf_visti, nomi_visti = set(), set()
    for r in atenei:
        if not r['nome'] or not r['regione'] or not r['tipo']:
            raise ValueError(f'Riga incompleta: {r}')
        nome_norm = normalizza(r['nome'])
        if nome_norm in nomi_visti:
            raise ValueError(f'Nome ateneo duplicato nell\'anagrafe: {r["nome"]}')
        nomi_visti.add(nome_norm)
        cf = r['codice_fiscale']
        if cf:
            if not (len(cf) == 11 and cf.isdigit()):
                raise ValueError(f'Codice fiscale non valido per {r["nome"]}: {cf}')
            if cf in cf_visti:
                raise ValueError(f'Codice fiscale duplicato in anagrafe: {cf}')
            cf_visti.add(cf)
    return atenei


def calcola(dati, atenei):
    by_cf = defaultdict(list)
    by_nome = defaultdict(set)
    for u in dati.unita:
        by_cf[u.cf].append(u)
        by_nome[normalizza(u.ente)].add(chiave_ente(u))

    result = []
    for r in atenei:
        cf = r['codice_fiscale']
        if cf:
            corrispondenze = by_cf.get(cf, [])
            metodo = 'codice fiscale' if corrispondenze else 'nessuna'
        else:
            # Evita unioni approssimative: es. Bergamo/"Teramo".
            keys = by_nome.get(normalizza(r['nome']), set())
            if len(keys) > 1:
                raise ValueError(f'Nome ambiguo per {r["nome"]}, fornire codice fiscale')
            corrispondenze = [u for u in dati.unita if chiave_ente(u) in keys] if keys else []
            metodo = 'nome esatto normalizzato' if corrispondenze else 'nessuna'

        progetti = {(u.settore, u.progetto) for u in corrispondenze}
        pi = sum(u.ruolo == 'PI' for u in corrispondenze)
        ru = sum(u.ruolo == 'RU' for u in corrispondenze)
        finanziamento = sum((u.mur for u in corrispondenze), Decimal(0))
        result.append({**r, 'PI': pi, 'RU': ru, 'progetti': len(progetti),
                       'mur': finanziamento, 'presente': bool(corrispondenze),
                       'metodo': metodo})
    result.sort(key=lambda r: (r['regione'].casefold(), r['nome'].casefold()))
    return result


def safe(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def riepilogo(righe, tipo):
    c = Counter(r['regione' if tipo == 'regione' else 'tipo'] for r in righe)
    no = Counter(r['regione' if tipo == 'regione' else 'tipo'] for r in righe if not r['presente'])
    items = sorted(c, key=lambda s: (-(no[s]), s.casefold()))
    title = 'Regione' if tipo == 'regione' else 'Tipologia'
    lines = [f'| {title} | Atenei censiti | Nessuna partecipazione | Con partecipazione |',
             '|---|---:|---:|---:|']
    for key in items:
        lines.append(f'| {safe(key)} | {c[key]} | {no[key]} | {c[key]-no[key]} |')
    return lines


def crea_markdown(dati, righe):
    assenti = [r for r in righe if not r['presente']]
    no_pi = [r for r in righe if r['PI'] == 0]
    attivi = [r for r in righe if r['presente']]
    lines = [
        '# PRIN 2026 – Atenei italiani senza progetti finanziati nei dati disponibili', '',
        f'**File Excel analizzati:** {len(dati.file)}; **progetti complessivi (anche enti non universitari):** {len(dati.progetti)}.  ',
        f'**Istituzioni nell\'anagrafe di riferimento:** {len(righe)}.  ',
        f'**Atenei con almeno una partecipazione PI/RU:** {len(attivi)}.  ',
        f'**Atenei senza alcuna partecipazione PI/RU:** {len(assenti)}.  ',
        f'**Atenei senza coordinamenti PI (possono essere RU):** {len(no_pi)}.', '',
        '## Atenei senza alcun progetto come PI o RU', '',
        '| Regione | Ateneo | Tipo |', '|---|---|---|',
    ]
    for r in assenti:
        lines.append(f"| {safe(r['regione'])} | {safe(r['nome'])} | {safe(r['tipo'])} |")
    lines += ['', '## Distribuzione per regione', ''] + riepilogo(righe, 'regione')
    lines += ['', '## Distribuzione per tipo di istituzione', ''] + riepilogo(righe, 'tipo')
    lines += ['', '## Atenei presenti come RU ma mai come PI', '',
              '| Regione | Ateneo | RU (unità) | MUR RU (EUR) |', '|---|---|---:|---:|']
    solo_ru = [r for r in righe if r['RU'] and not r['PI']]
    for r in solo_ru:
        lines.append(f"| {safe(r['regione'])} | {safe(r['nome'])} | {r['RU']} | {euro(r['mur'])} |")
    if not solo_ru:
        lines.append('| — | Nessuno | — | — |')
    lines += ['', '## Criterio e fonti', '',
              '- **Senza progetti** significa che l\'ateneo non compare in nessuna delle unità PI o RU **dei file Excel analizzati**, non che abbia partecipato senza vincere.',
              '- I progetti sono 161 distribuiti nei 20 settori attualmente caricati. Settori/bandi non presenti nei file non sono stati valutati.',
              '- I dati delle partecipazioni provengono dai file Excel del progetto; il criterio è l\'assenza di **qualsiasi** partecipazione come PI o RU.',
              '- Anagrafe degli atenei: [USTAT – Tutti gli atenei](' + URL_USTAT + ') (100 voci) e [MUR – Università non statali riconosciute](' + URL_MUR + ') (integrazione UNINEUROMED; pagina aggiornata nel gennaio 2026).',
              '- Il file `data/atenei_italiani.csv` è uno **snapshot locale modificabile**: per aggiungere o rimuovere enti è necessario aggiornarlo. Non viene aggiornato automaticamente.',
              '- I codici fiscali popolati nell\'anagrafe sono ricavati dalle righe degli Excel PRIN; il confronto per CF evita errori dovuti alle varianti di denominazione. Senza CF si usa solo la corrispondenza esatta dopo normalizzazione, mai una somiglianza fuzzy.',
              '- Gli enti di ricerca non universitari (es. CNR, INFN) non entrano nel denominatore. Sono invece comprese le scuole superiori ad ordinamento speciale elencate da USTAT, le telematiche e le non statali.',
              '- L\'assenza di partecipazioni **non** fornisce informazioni sul numero di domande presentate, né sul tasso di successo.', '']
    if dati.avvisi:
        lines += ['## Note sui file sorgente', ''] + ['- '+safe(s) for s in dati.avvisi] + ['']
    return '\n'.join(lines)


def salva_csv(path, righe, tutto=False):
    fields = ['Ateneo', 'Regione', 'Tipo', 'Codice fiscale', 'Fonte elenco']
    if tutto:
        fields += ['PI', 'RU', 'Progetti distinti', 'MUR EUR', 'Presente', 'Metodo confronto']
    with path.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(fields)
        for r in righe:
            values = [r['nome'], r['regione'], r['tipo'], r['codice_fiscale'], r['fonte']]
            if tutto:
                values += [r['PI'], r['RU'], r['progetti'], str(r['mur']),
                           'SI' if r['presente'] else 'NO', r['metodo']]
            writer.writerow(values)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', type=Path, default=DATA_DIR, help='Cartella file Excel; percorso relativo alla root')
    p.add_argument('--atenei', type=Path, default=Path('data/atenei_italiani.csv'), help='Anagrafe CSV degli atenei')
    p.add_argument('--md', type=Path, default=Path('atenei_senza_progetti.md'), help='Report Markdown')
    p.add_argument('--csv-dir', type=Path, default=Path('.'), help='Directory dei CSV, relativa alla root')
    args = p.parse_args()
    data = carica_dataset(destinazione(args.data))
    roster = leggi_anagrafe(destinazione(args.atenei))
    righe = calcola(data, roster)
    assenti = [r for r in righe if not r['presente']]
    md, csv_dir = destinazione(args.md), destinazione(args.csv_dir)
    md.parent.mkdir(parents=True, exist_ok=True)
    csv_dir.mkdir(parents=True, exist_ok=True)
    md.write_text(crea_markdown(data, righe), encoding='utf-8')
    path_no = csv_dir / 'atenei_senza_progetti.csv'
    path_all = csv_dir / 'partecipazione_atenei_italiani.csv'
    salva_csv(path_no, assenti)
    salva_csv(path_all, righe, tutto=True)
    print(f'Elenco ufficiale di riferimento: {len(righe)} atenei')
    print(f'File Excel: {len(data.file)}; progetti finanziati: {len(data.progetti)}')
    print(f'Senza partecipazioni PI/RU: {len(assenti)}; con partecipazioni: {len(righe)-len(assenti)}')
    print(f'Markdown: {md}\nCSV: {path_no}\nCSV: {path_all}')
    for avviso in data.avvisi:
        print(f'AVVISO: {avviso}', file=sys.stderr)


if __name__ == '__main__':
    main()
