"""Two public figures for the full 2021–June 2026 company-media atlas post.

Read the saved post facts only. Preserve the completed linkage and old figures.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import FuncNorm, LinearSegmentedColormap
from matplotlib.transforms import blended_transform_factory

ROOT = Path(__file__).resolve().parents[1]
FACTS = ROOT / 'outputs/facts/gfi_media_atlas_post.json'
OUT = ROOT / 'outputs/figures/gfi_media_atlas_post'
POST_IMAGES = ROOT / 'posts/2026-09-firme-u-medijima/images'
PALETTE_FILE = ROOT / 'R/house_style.R'
SEED = 20260918
PAL = dict(re.findall(r'^\s+(\w+)\s*=\s*"(#[A-Fa-f0-9]{6})"',
                      PALETTE_FILE.read_text(encoding='utf-8'), re.M))
assert {'paper', 'ink', 'muted', 'hair', 'accent', 'amber', 'surface'} <= PAL.keys()
plt.rcParams.update({
    'font.family': 'monospace', 'font.monospace': ['DejaVu Sans Mono'],
    'figure.facecolor': PAL['paper'], 'axes.facecolor': PAL['paper'],
    'savefig.facecolor': PAL['paper'], 'text.color': PAL['ink'],
    'axes.labelcolor': PAL['muted'], 'xtick.color': PAL['muted'],
    'ytick.color': PAL['muted'], 'axes.edgecolor': PAL['hair'],
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.spines.left': False, 'axes.spines.bottom': False,
    'xtick.major.size': 0, 'ytick.major.size': 0,
    'svg.fonttype': 'none', 'font.size': 12,
})
SOURCE = 'Izvor. GFI, medijski arhiv i AEM-ov popis elektroničkih publikacija. Izračun AI.econ.'


def nhr(value: int) -> str:
    return f'{int(value):,}'.replace(',', '.')


def phr(value: float) -> str:
    return f'{value:.1f}'.replace('.', ',')


def save(fig, stem: str) -> list[str]:
    paths = []
    for suffix in ('png', 'svg'):
        path = OUT / f'{stem}.{suffix}'
        fig.savefig(path, dpi=180, facecolor=PAL['paper'])
        assert path.stat().st_size > 1000
        shutil.copyfile(path, POST_IMAGES / path.name)
        paths.append(path.relative_to(ROOT).as_posix())
    plt.close(fig)
    return paths


def label_name(name: str) -> str:
    short = re.sub(r',?\s+(?:j\.d\.o\.o\.|d\.o\.o\.|d\.d\.|k\.d\.)\s*$', '', name,
                   flags=re.IGNORECASE).strip()
    return short if len(short) <= 40 else short[:39].rstrip() + '…'


def monthly_array(firm: dict, months: list[str]) -> np.ndarray:
    rows = {r['month']: r for r in firm['monthly']}
    assert set(rows) == set(months), f"Incomplete firm-month grid for {firm['name']}"
    values = np.array([int(rows[m]['articles']) for m in months], dtype=int)
    assert (values >= 0).all()
    return values


def save_paths(facts: dict) -> dict:
    coverage = [r for r in facts['coverage_monthly']['media'] if r['month'] >= '2025-01']
    months = [r['month'] for r in coverage]
    assert len(months) == 18 and months[-1] == '2026-06'
    assert all(r['body_pct'] == 100 for r in coverage)
    keys = ('aci', 'konzum', 'ina', 'podravka', 'bosqar', 'eurco', 'koncar_ev')
    names = ('ACI', 'Konzum plus', 'INA', 'Podravka', 'BOSQAR', 'EURCO', 'Končar Električna vozila')
    rows = [facts['cases'][key] for key in keys]
    values = np.vstack([monthly_array({'name': r['name'], 'monthly': [m for m in r['monthly']
                       if m['month'] >= '2025-01']}, months) for r in rows])
    maximum = int(values.max())
    cmap = LinearSegmentedColormap.from_list('house_sequential', [PAL['paper'], PAL['accent']])
    norm = FuncNorm((np.log1p, np.expm1), vmin=0, vmax=maximum)
    fig = plt.figure(figsize=(16, 8))
    ax = fig.add_axes([.265, .29, .695, .48])
    mesh = ax.imshow(values, cmap=cmap, norm=norm, interpolation='nearest', aspect='auto')
    ax.set_yticks(range(len(rows)), names, fontsize=12)
    ax.tick_params(axis='y', pad=12)
    ax.set_xticks(range(len(months)), [m[5:] for m in months], fontsize=11)
    ax.tick_params(axis='x', pad=9)
    for x in np.arange(-.5, len(months), 1):
        ax.axvline(x, color=PAL['paper'], linewidth=1.4)
    for y in np.arange(-.5, len(rows), 1):
        ax.axhline(y, color=PAL['paper'], linewidth=1.4)
    ax.axvline(11.5, color=PAL['ink'], linewidth=1.2)
    transform = blended_transform_factory(ax.transData, ax.transAxes)
    for x, label in ((5.5, '2025.'), (14.5, '2026. · siječanj–lipanj')):
        ax.text(x, 1.06, label, transform=transform, ha='center', fontsize=12, weight='bold')
    for yi, row in enumerate(values):
        for xi, value in enumerate(row):
            ax.text(xi, yi, str(value), ha='center', va='center', fontsize=10,
                    color=PAL['paper'] if norm(value) > .58 else PAL['ink'])
    cax = fig.add_axes([.265, .16, .695, .021])
    bar = fig.colorbar(mesh, cax=cax, orientation='horizontal')
    ticks = [v for v in (0, 1, 3, 10, 30, 100) if v <= maximum]
    if maximum not in ticks:
        ticks.append(maximum)
    bar.set_ticks(ticks, labels=[nhr(n) for n in ticks])
    bar.outline.set_edgecolor(PAL['hair'])
    bar.set_label('Članci po firmi i mjesecu · zajednička logaritamska ljestvica boje', fontsize=10, labelpad=8)
    fig.text(.04, .955, 'Neka se imena vraćaju, druga izdvajaju pojedini mjeseci.',
             fontsize=18, weight='bold', va='top')
    fig.text(.04, .895, 'Siječanj 2025. → lipanj 2026. · izbor firmi iz teksta · broj u polju pokazuje broj članaka',
             fontsize=11, color=PAL['muted'], va='top')
    fig.text(.04, .051, 'Pratimo pojedine pravne osobe. Končar Električna vozila prikazan je odvojeno od grupe Končar.',
             fontsize=9.5, color=PAL['muted'])
    fig.text(.04, .02, SOURCE, fontsize=9, color=PAL['muted'])
    return {'files': save(fig, 'firm_paths_2025_2026'), 'scope': 'media',
            'selected_firms': [{'oib': r['oib'], 'name': names[i], 'selection': 'named_post_case',
                                'monthly_articles': values[i].tolist()} for i, r in enumerate(rows)],
            'months': months, 'common_color_max': maximum}


def save_persistence(facts: dict) -> dict:
    hist = {int(r['active_months']): int(r['firms']) for r in facts['persistence']['histogram']}
    denominator = int(facts['overview']['media']['covered_firms'])
    assert sum(hist.values()) == denominator
    definitions = [(1, 1, '1 mjesec'), (2, 3, '2–3 mjeseca'), (4, 11, '4–11 mjeseci'),
                   (12, 35, '12–35 mjeseci'), (36, 66, '36–66 mjeseci')]
    data = [{'minimum': lo, 'maximum': hi, 'label': label,
             'firms': sum(hist.get(i, 0) for i in range(lo, hi + 1))}
            for lo, hi, label in definitions]
    for row in data:
        row['share_pct'] = row['firms'] / denominator * 100
    first_three = sum(hist.get(i, 0) for i in range(1, 4))
    share = first_three / denominator * 100
    assert 74.5 <= share <= 75.5, 'The rounded three-in-four title no longer fits this dataset'
    fig, ax = plt.subplots(figsize=(14.22, 8))
    fig.subplots_adjust(left=.22, right=.92, top=.78, bottom=.23)
    y = np.arange(len(data))
    ax.barh(y, [r['firms'] for r in data], height=.59,
            color=[PAL['accent'], PAL['accent'], PAL['muted'], PAL['muted'], PAL['muted']])
    ax.invert_yaxis()
    ax.set_yticks(y, [r['label'] for r in data], fontsize=12.5)
    ax.set_xlim(0, max(r['firms'] for r in data) * 1.32)
    ticks = [0, 2000, 4000, 6000, 8000]
    ax.set_xticks(ticks, [nhr(n) for n in ticks], fontsize=10.5)
    ax.grid(axis='x', color=PAL['hair'], linewidth=.8)
    ax.set_axisbelow(True)
    ax.set_xlabel('Broj firmi', fontsize=11, labelpad=12)
    for i, row in enumerate(data):
        ax.text(row['firms'] + 140, i, f"{nhr(row['firms'])}  ({phr(row['share_pct'])} %)",
                va='center', fontsize=12, weight='bold' if i < 2 else 'normal')
    fig.text(.04, .959, 'Tri od četiri prepoznate firme nalazimo u najviše tri mjeseca.',
             fontsize=16.5, weight='bold', va='top')
    fig.text(.04, .907, f"2021. → lipanj 2026. · {nhr(denominator)} firmi s barem jednim prepoznatim spominjanjem",
             fontsize=11, color=PAL['muted'], va='top')
    fig.text(.04, .135, 'Skupine mjeseci nejednake su duljine. Jedan mjesec znači barem jedan prepoznat članak u tom mjesecu.',
             fontsize=9.5, color=PAL['muted'])
    fig.text(.04, .096, 'Brojimo različite mjesece sa spominjanjem. Ti mjeseci ne moraju biti uzastopni.',
             fontsize=9.5, color=PAL['muted'])
    fig.text(.04, .045, SOURCE, fontsize=9, color=PAL['muted'])
    return {'files': save(fig, 'firm_persistence_2021_2026'), 'scope': 'media',
            'denominator': denominator, 'at_most_three_months': first_three,
            'at_most_three_months_share_pct': share, 'categories': data}


def main() -> None:
    np.random.seed(SEED)
    source_bytes = FACTS.read_bytes()
    facts = json.loads(source_bytes)
    assert all(facts['checks'].values())
    OUT.mkdir(parents=True, exist_ok=True)
    POST_IMAGES.mkdir(parents=True, exist_ok=True)
    results = {'paths': save_paths(facts), 'persistence': save_persistence(facts)}
    manifest = {'source': FACTS.relative_to(ROOT).as_posix(),
                'source_sha256': hashlib.sha256(source_bytes).hexdigest(),
                'palette_source': PALETTE_FILE.relative_to(ROOT).as_posix(),
                'palette_sha256': hashlib.sha256(PALETTE_FILE.read_bytes()).hexdigest(),
                'seed': SEED, 'figures': results, 'rendered': True}
    (OUT / 'chart_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({key: value['files'] for key, value in results.items()}, indent=2))


if __name__ == '__main__':
    main()
