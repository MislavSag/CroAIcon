"""Build five static public atlas pages from saved monthly counts.

No source database, browser-side data, article evidence or identifier is published.
"""
import csv
import hashlib
import json
import math
import re
import shutil
from collections import defaultdict
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / 'outputs/tables/gfi_media_longitudinal'
FACTS = ROOT / 'outputs/facts/gfi_media_atlas_post.json'
TEMPLATE = ROOT / 'python/templates/gfi_media_atlas_public.html'
PALETTE = ROOT / 'R/house_style.R'
OUT = ROOT / 'outputs/figures/gfi_media_atlas_post/pages'
POST = ROOT / 'posts/2026-09-firme-u-medijima/atlas'
PUBLIC_FACTS = ROOT / 'outputs/facts/gfi_media_atlas_public.json'
PAGE_COUNT = 5
PAGE_SIZE = 30


def read_csv(name):
    with (TABLES / f'{name}.csv').open(encoding='utf-8-sig', newline='') as handle:
        yield from csv.DictReader(handle)


def number(value):
    return f'{int(value):,}'.replace(',', '.')


def filename(page):
    return 'index.html' if page == 1 else f'stranica-{page}.html'


def navigation(page):
    items = []
    for i in range(1, PAGE_COUNT + 1):
        if i == page:
            items.append(f'<span aria-current="page">{i}</span>')
        else:
            items.append(f'<a href="{filename(i)}" aria-label="Stranica {i}">{i}</a>')
    return '<nav class="pages" aria-label="Stranice pregleda">' + ''.join(items) + '</nav>'


def main():
    facts = json.loads(FACTS.read_text(encoding='utf-8'))
    months = [r['month'] for r in facts['coverage_monthly']['media'] if r['month'] >= '2025-01']
    assert len(months) == 18 and months[-1] == '2026-06'
    assert all(r['body_pct'] == 100 for r in facts['coverage_monthly']['media'] if r['month'] in months)
    names = {r['oib']: r['display_name'] for r in read_csv('firms')}
    values = defaultdict(lambda: [0] * len(months))
    month_index = {m: i for i, m in enumerate(months)}
    for row in read_csv('firm_month'):
        month = row['month'][:7]
        if row['scope'] == 'media' and month in month_index:
            values[row['oib']][month_index[month]] += int(row['articles'])
    ranked = sorted(values, key=lambda oib: (-sum(values[oib]), oib))
    selected = [{'rank': i, 'oib': oib, 'name': names[oib], 'monthly_articles': values[oib],
                 'total_articles': sum(values[oib])}
                for i, oib in enumerate(ranked[:PAGE_COUNT * PAGE_SIZE], 1)]
    assert len(selected) == 150 and len({r['oib'] for r in selected}) == 150
    for year in (2025, 2026):
        indices = [i for i, m in enumerate(months) if m.startswith(str(year))]
        expected = next(r for r in facts['annual_coverage']['media'] if r['year'] == year)
        assert sum(any(row[i] for i in indices) for row in values.values()) == expected['covered_firms']
        assert sum(row[i] for row in values.values() for i in indices) == expected['links']
    public_facts = {'months': months, 'pages': PAGE_COUNT, 'firms_per_page': PAGE_SIZE,
                    'selected_firms': len(selected), 'firms': selected,
                    'selection': 'Top 150 by accepted media article–firm links, January 2025–June 2026; OIB tie-break.',
                    'inputs': {f'outputs/tables/gfi_media_longitudinal/{name}.csv':
                               hashlib.sha256((TABLES / f'{name}.csv').read_bytes()).hexdigest()
                               for name in ('firms', 'firm_month')}}
    PUBLIC_FACTS.write_text(json.dumps(public_facts, ensure_ascii=False, indent=2), encoding='utf-8')
    palette = dict(re.findall(r'^\s+(\w+)\s*=\s*"(#[A-Fa-f0-9]{6})"',
                              PALETTE.read_text(encoding='utf-8'), re.M))
    rgb = lambda colour: tuple(int(colour[i:i+2], 16) for i in (1, 3, 5))
    base, accent = rgb(palette['paper']), rgb(palette['accent'])
    maximum = max(v for firm in selected for v in firm['monthly_articles'])
    template = TEMPLATE.read_text(encoding='utf-8')
    headers = ''.join(f'<th scope="col" class="{"year" if i == 12 else ""}">{m[5:]}.<br>{m[:4]}.</th>'
                      for i, m in enumerate(months))
    OUT.mkdir(parents=True, exist_ok=True)
    POST.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for page in range(1, PAGE_COUNT + 1):
        rows = []
        subset = selected[(page-1)*PAGE_SIZE:page*PAGE_SIZE]
        for firm in subset:
            cells = []
            for i, value in enumerate(firm['monthly_articles']):
                intensity = math.log1p(value) / math.log1p(maximum)
                colour = ','.join(str(round(a + (b-a)*intensity)) for a, b in zip(base, accent))
                foreground = palette['paper'] if intensity > .58 else palette['ink']
                cells.append(f'<td class="cell {"year" if i == 12 else ""}" '
                             f'style="background:rgb({colour});color:{foreground}">{number(value)}</td>')
            rows.append(f'<tr><th scope="row" class="name"><span class="rank">{firm["rank"]}.</span> '
                        f'{escape(firm["name"])}</th>{"".join(cells)}'
                        f'<td class="total">{number(firm["total_articles"])}</td></tr>')
        replacements = {'__PALETTE__': ';'.join(f'--{key}:{value}' for key, value in palette.items()),
                        '__PAGE__': str(page), '__FIRST__': str(subset[0]['rank']),
                        '__LAST__': str(subset[-1]['rank']), '__NAVIGATION__': navigation(page),
                        '__MAXIMUM__': number(maximum), '__HEADERS__': headers, '__ROWS__': ''.join(rows)}
        html = template
        for key, value in replacements.items():
            html = html.replace(key, value)
        assert not re.search(r'__[A-Z]+__', html)
        path = OUT / filename(page)
        path.write_text(html, encoding='utf-8')
        shutil.copyfile(path, POST / path.name)
        hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = {'pages': hashes, 'page_count': PAGE_COUNT, 'firms_per_page': PAGE_SIZE,
                'selected_firms': len(selected), 'months': months, 'common_colour_max': maximum,
                'facts_sha256': hashlib.sha256(PUBLIC_FACTS.read_bytes()).hexdigest(),
                'template_sha256': hashlib.sha256(TEMPLATE.read_bytes()).hexdigest(),
                'counts_reconciled': True, 'javascript': False, 'article_evidence': False}
    (OUT.parent / 'public_pages_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
