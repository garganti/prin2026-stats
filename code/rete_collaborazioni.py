#!/usr/bin/env python3
"""Rete di collaborazione tra enti che partecipano agli stessi progetti PRIN.

Crea un arco non orientato per ogni coppia di enti distinti nello stesso progetto.
Il peso misura il numero di progetti condivisi; PI-RU/RU-RU sono classificati
secondo i ruoli assunti dalle due istituzioni nel progetto.
Calcola grado, forza del nodo e betweenness non pesata (algoritmo di Brandes).
"""
import argparse
import csv
import sys
from collections import defaultdict, deque
from decimal import Decimal
from itertools import combinations
from pathlib import Path

from prin_data import PROJECT_ROOT, DATA_DIR, carica_dataset, chiave_ente, euro, nome_ente


def destinazione(percorso):
    p = Path(percorso)
    return p if p.is_absolute() else PROJECT_ROOT / p


def betweenness(adjacency):
    """Centralita di intermediazione normalizzata [0,1], non pesata, non orientata."""
    nodes = sorted(adjacency)
    n = len(nodes)
    centrality = {v: 0.0 for v in nodes}
    for s in nodes:
        stack = []
        preds = {v: [] for v in nodes}
        sigma = dict.fromkeys(nodes, 0.0)
        sigma[s] = 1.0
        dist = dict.fromkeys(nodes, -1)
        dist[s] = 0
        q = deque([s])
        while q:
            v = q.popleft()
            stack.append(v)
            for w in adjacency[v]:
                if dist[w] < 0:
                    q.append(w)
                    dist[w] = dist[v] + 1
                if dist[w] == dist[v] + 1:
                    sigma[w] += sigma[v]
                    preds[w].append(v)
        delta = dict.fromkeys(nodes, 0.0)
        while stack:
            w = stack.pop()
            for v in preds[w]:
                delta[v] += sigma[v] / sigma[w] * (1.0 + delta[w])
            if w != s:
                centrality[w] += delta[w]
    if n <= 2:
        return centrality
    scale = 1.0 / ((n - 1) * (n - 2))  # half for undirected, then normalize to 1
    return {v: x * scale for v, x in centrality.items()}


def componenti(adjacency):
    unseen = set(adjacency)
    groups = []
    while unseen:
        start = min(unseen)
        seen = {start}
        q = [start]
        while q:
            v = q.pop()
            for u in adjacency[v]:
                if u not in seen:
                    seen.add(u)
                    q.append(u)
        unseen -= seen
        groups.append(seen)
    return sorted(groups, key=len, reverse=True)


def analizza(dati):
    nodes = defaultdict(lambda: {'nomi': set(), 'ruoli': defaultdict(int),
                                 'mur': Decimal(0), 'settori': set(), 'progetti': set()})
    projects = defaultdict(list)
    for u in dati.unita:
        key = chiave_ente(u)
        node = nodes[key]
        node['nomi'].add(u.ente)
        node['ruoli'][u.ruolo] += 1
        node['mur'] += u.mur
        node['settori'].add(u.settore)
        node['progetti'].add((u.settore, u.progetto))
        projects[(u.settore, u.progetto)].append(u)

    edges = defaultdict(lambda: {'progetti': set(), 'pi_ru': 0, 'ru_ru': 0})
    for project, units in projects.items():
        roles = defaultdict(set)
        for u in units:
            roles[chiave_ente(u)].add(u.ruolo)
        for a, b in combinations(sorted(roles), 2):
            r = edges[(a, b)]
            r['progetti'].add(project)
            if ('PI' in roles[a] and 'RU' in roles[b]) or ('RU' in roles[a] and 'PI' in roles[b]):
                r['pi_ru'] += 1
            if 'RU' in roles[a] and 'RU' in roles[b]:
                r['ru_ru'] += 1
    adjacency = {key: set() for key in nodes}
    strength = defaultdict(int)
    for (a, b), e in edges.items():
        adjacency[a].add(b)
        adjacency[b].add(a)
        strength[a] += len(e['progetti'])
        strength[b] += len(e['progetti'])
    bt = betweenness(adjacency)
    n = len(nodes)
    node_rows = []
    for key, v in nodes.items():
        node_rows.append({'key': key, 'ente': nome_ente(v['nomi']),
                          'cf': key[1] if key[0] == 'cf' else '',
                          'pi': v['ruoli']['PI'], 'ru': v['ruoli']['RU'],
                          'progetti': len(v['progetti']), 'settori': len(v['settori']),
                          'mur': v['mur'], 'grado': len(adjacency[key]),
                          'grado_norm': len(adjacency[key]) / (n - 1) if n > 1 else 0,
                          'forza': strength[key], 'betweenness': bt[key]})
    node_rows.sort(key=lambda r: (-r['grado'], -r['forza'], r['ente'].casefold()))
    labels = {row['key']: row['ente'] for row in node_rows}
    edge_rows = []
    for (a, b), r in edges.items():
        edge_rows.append({'a': labels[a], 'b': labels[b], 'peso': len(r['progetti']),
                          'pi_ru': r['pi_ru'], 'ru_ru': r['ru_ru'],
                          'progetti': sorted(f'{sec}:{cod}' for sec, cod in r['progetti'])})
    edge_rows.sort(key=lambda r: (-r['peso'], r['a'].casefold(), r['b'].casefold()))
    assert len(projects) == len(dati.progetti)
    return node_rows, edge_rows, componenti(adjacency)


def crea_report(dati, nodes, edges, comps):
    pairs_repeated = sum(e['peso'] > 1 for e in edges)
    total_piru = sum(e['pi_ru'] for e in edges)
    total_ruru = sum(e['ru_ru'] for e in edges)
    by_bridge = sorted(nodes, key=lambda r: (-r['betweenness'], -r['grado'], r['ente'].casefold()))
    lines = [
        '# PRIN 2026 - Rete delle collaborazioni tra universita ed enti', '',
        f'**Settori/file:** {len(dati.file)}  ',
        f'**Progetti:** {len(dati.progetti)}  ',
        f'**Nodi (enti distinti):** {len(nodes)}  ',
        f'**Archi (coppie di enti):** {len(edges)}  ',
        f'**Coppie ricorrenti (almeno 2 progetti):** {pairs_repeated}  ',
        f'**Collaborazioni progetto-coppia PI-RU:** {total_piru}  ',
        f'**Collaborazioni progetto-coppia RU-RU:** {total_ruru}  ',
        f'**Componenti connesse:** {len(comps)}; massima: {len(comps[0]) if comps else 0} enti', '',
        '## Enti con piu partner diversi', '',
        '| Ateneo / Ente | Partner distinti (grado) | Forza (progetti-coppia) | Intermediazione | Progetti |',
        '|---|---:|---:|---:|---:|',
    ]
    for n in nodes[:30]:
        lines.append(f"| {n['ente'].replace('|', '/')} | {n['grado']} | {n['forza']} | "
                     f"{n['betweenness']:.4f} | {n['progetti']} |")
    lines.extend(['', '## Principali collaborazioni ricorrenti', '',
                  '| Ateneo / Ente A | Ateneo / Ente B | Progetti condivisi | PI-RU | RU-RU |',
                  '|---|---|---:|---:|---:|'])
    for e in [x for x in edges if x['peso'] >= 2][:40]:
        lines.append(f"| {e['a'].replace('|', '/')} | {e['b'].replace('|', '/')} | "
                     f"{e['peso']} | {e['pi_ru']} | {e['ru_ru']} |")
    if not pairs_repeated:
        lines.append('| (nessuna collaborazione ripetuta) | - | - | - | - |')
    lines.extend(['', '## Enti ponte: maggiore intermediazione', '',
                  '| Ateneo / Ente | Intermediazione normalizzata | Partner distinti |',
                  '|---|---:|---:|'])
    for n in by_bridge[:20]:
        lines.append(f"| {n['ente'].replace('|', '/')} | {n['betweenness']:.4f} | {n['grado']} |")
    lines.extend(['', '## Metodo e interpretazione', '',
                  '- Rete **non orientata**: due enti sono collegati quando almeno una loro unita partecipa allo stesso progetto.',
                  '- Un arco conta ogni progetto condiviso **una sola volta**, anche con piu unita per ente.',
                  '- Il **grado** e il numero di partner istituzionali distinti; la **forza** somma i progetti condivisi sui vari partner.',
                  '- I tipi PI-RU e RU-RU contano le collaborazioni per coppia di enti in un progetto; una coppia puo essere classificata in entrambe le categorie solo se i ruoli lo consentono.',
                  '- **Intermediazione (betweenness)**: frazione normalizzata dei cammini minimi che attraversano l\'ente, senza pesare gli archi; non e una misura di qualita scientifica.',
                  '- CSV completi: nodi (tutti gli enti) e archi (tutte le coppie), con codici dei progetti condivisi.', ''])
    if dati.avvisi:
        lines.extend(['## Avvisi relativi ai dati sorgente', ''] + [f'- {a}' for a in dati.avvisi] + [''])
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=DATA_DIR, help='Cartella XLSX')
    parser.add_argument('--md', type=Path, default=Path('rete_collaborazioni.md'))
    parser.add_argument('--csv-dir', type=Path, default=Path('.'))
    args = parser.parse_args()
    dati = carica_dataset(destinazione(args.data))
    nodes, edges, comps = analizza(dati)
    md = destinazione(args.md)
    csv_dir = destinazione(args.csv_dir)
    md.parent.mkdir(parents=True, exist_ok=True)
    csv_dir.mkdir(parents=True, exist_ok=True)
    md.write_text(crea_report(dati, nodes, edges, comps), encoding='utf-8')
    path_nodes = csv_dir / 'rete_collaborazioni_nodi.csv'
    with path_nodes.open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['Ente', 'Codice fiscale', 'Partecipazioni PI', 'Partecipazioni RU',
                    'Progetti distinti', 'Settori distinti', 'MUR totale EUR', 'Grado',
                    'Grado normalizzato', 'Forza', 'Betweenness normalizzata'])
        for r in nodes:
            w.writerow([r['ente'], r['cf'], r['pi'], r['ru'], r['progetti'], r['settori'],
                        str(r['mur']), r['grado'], f"{r['grado_norm']:.6f}", r['forza'],
                        f"{r['betweenness']:.6f}"])
    path_edges = csv_dir / 'rete_collaborazioni_archi.csv'
    with path_edges.open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['Ente A', 'Ente B', 'Numero progetti condivisi',
                    'Progetti PI-RU', 'Progetti RU-RU', 'Elenco progetti (settore:codice)'])
        for r in edges:
            w.writerow([r['a'], r['b'], r['peso'], r['pi_ru'], r['ru_ru'], '|'.join(r['progetti'])])
    print(f'OK {len(dati.file)} file, {len(nodes)} enti, {len(edges)} collaborazioni; componenti: {len(comps)}')
    print(f'Markdown: {md}\nCSV: {path_nodes}\nCSV: {path_edges}')
    for avviso in dati.avvisi:
        print(f'AVVISO: {avviso}', file=sys.stderr)


if __name__ == '__main__':
    main()
