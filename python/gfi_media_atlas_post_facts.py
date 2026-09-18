"""Build full-period blog facts exclusively from the frozen, saved CSV outputs.

No source database, dictionary, labels or earlier facts are read or modified.
All mentions are accepted publisher-article/firm pairs, not word frequencies.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / 'outputs/tables/gfi_media_longitudinal'
TARGET = ROOT / 'outputs/facts/gfi_media_atlas_post.json'
SCOPES = ('broad', 'media', 'stable')
SELECTION_YEAR = 2023
TOP_ROWS = 100
CASES = {'aci': '17195049659', 'konzum': '62226620908', 'eurco': '25484937943',
         'koncar_ev': '66253945791', 'bosqar': '62230095889'}
INPUTS = ('firms', 'firm_month', 'firm_period', 'firm_persistence', 'firm_publishers',
          'yearly_summary', 'monthly_summary', 'coverage_month', 'concentration', 'common_publishers')


def read_csv(name):
    with (TABLES / f'{name}.csv').open(encoding='utf-8-sig', newline='') as handle:
        yield from csv.DictReader(handle)


def numeric(row, integer_fields=(), float_fields=()):
    result = dict(row)
    for key in integer_fields:
        result[key] = int(result[key])
    for key in float_fields:
        result[key] = float(result[key])
    return result


def change_pct(before, after):
    return 100 * (after / before - 1) if before else None


def main():
    input_before = {name: (TABLES / f'{name}.csv').stat().st_mtime_ns for name in INPUTS}
    firms = {r['oib']: r for r in read_csv('firms')}
    # Resolve these familiar examples from saved legal names, never brand guesses.
    for key, name in (('ina', 'INA, d.d.'), ('podravka', 'PODRAVKA d.d.')):
        matches = [oib for oib, row in firms.items() if row['display_name'] == name]
        assert len(matches) == 1
        CASES[key] = matches[0]
    monthly = defaultdict(dict)
    for raw in read_csv('firm_month'):
        r = numeric(raw, ('articles', 'headline_articles', 'outlets'))
        month = r['month'][:7]
        key = (r['scope'], r['oib'])
        assert month not in monthly[key] and r['articles'] > 0
        monthly[key][month] = {'month': month, **{k: r[k] for k in ('articles', 'headline_articles', 'outlets')}}
    persistence = {(r['scope'], r['oib']): numeric(r, ('active_months', 'articles', 'peak_month_articles'))
                   for r in read_csv('firm_persistence')}
    assert set(monthly) == set(persistence)
    for key, months in monthly.items():
        p = persistence[key]
        assert len(months) == p['active_months']
        assert sum(r['articles'] for r in months.values()) == p['articles']
        assert max(r['articles'] for r in months.values()) == p['peak_month_articles']
        assert min(months) == p['first_detected_month'][:7]
        assert max(months) == p['last_detected_month'][:7]

    periods = {}
    for raw in read_csv('firm_period'):
        r = numeric(raw, ('year', 'articles', 'headline_articles', 'outlets', 'active_months', 'exact_text_groups'))
        key = (r['scope'], r['year'], r['period'], r['oib'])
        assert key not in periods
        periods[key] = r
        selected = [m for month, m in monthly[(r['scope'], r['oib'])].items()
                    if int(month[:4]) == r['year'] and (r['period'] == 'year' or int(month[5:7]) <= 6)]
        assert sum(m['articles'] for m in selected) == r['articles']
        assert sum(m['headline_articles'] for m in selected) == r['headline_articles']
        assert len(selected) == r['active_months']
    grouped_periods = defaultdict(list)
    for (scope, year, period, _), row in periods.items():
        grouped_periods[(scope, year, period)].append(row)

    coverage = {scope: [] for scope in SCOPES}
    coverage_lookup = {}
    for raw in read_csv('coverage_month'):
        r = numeric(raw, ('documents', 'observed_days', 'publishers', 'documents_with_body', 'documents_with_title'), ('body_pct', 'title_pct'))
        r['month'] = r['month'][:7]
        coverage[r['scope']].append(r)
        coverage_lookup[(r['scope'], r['month'])] = r
    for scope in SCOPES:
        coverage[scope].sort(key=lambda r: r['month'])
    months = [r['month'] for r in coverage['media']]
    assert len(months) == 66 and months[0] == '2021-01' and months[-1] == '2026-06'
    assert all([r['month'] for r in coverage[s]] == months for s in SCOPES)

    month_totals = defaultdict(lambda: Counter())
    for (scope, _), rows in monthly.items():
        for month, r in rows.items():
            month_totals[(scope, month)].update({'covered_firms': 1, 'document_firm_links': r['articles'], 'headline_links': r['headline_articles']})
    for raw in read_csv('monthly_summary'):
        r = numeric(raw, ('documents', 'covered_firms', 'document_firm_links', 'headline_links'))
        key = (r['scope'], r['month'][:7])
        assert all(r[k] == month_totals[key][k] for k in ('covered_firms', 'document_firm_links', 'headline_links'))
        assert r['documents'] == coverage_lookup[key]['documents']

    years = {}
    for raw in read_csv('yearly_summary'):
        r = numeric(raw, ('year', 'covered_firms', 'document_firm_links', 'firms_at_least_three', 'firms_at_least_two_outlets', 'headline_links'))
        key = (r['scope'], r['year'], r['period'])
        firm_rows = grouped_periods[key]
        assert r['covered_firms'] == len(firm_rows)
        assert r['document_firm_links'] == sum(p['articles'] for p in firm_rows)
        assert r['headline_links'] == sum(p['headline_articles'] for p in firm_rows)
        assert r['firms_at_least_three'] == sum(p['articles'] >= 3 for p in firm_rows)
        assert r['firms_at_least_two_outlets'] == sum(p['outlets'] >= 2 for p in firm_rows)
        cov = [m for m in coverage[r['scope']] if int(m['month'][:4]) == r['year'] and (r['period'] == 'year' or int(m['month'][5:]) <= 6)]
        r['eligible_articles'] = sum(m['documents'] for m in cov)
        r['documents_with_body'] = sum(m['documents_with_body'] for m in cov)
        r['body_pct'] = 100 * r['documents_with_body'] / r['eligible_articles']
        r['months'] = len(cov)
        r['links'] = r['document_firm_links']
        r['links_per_10000_articles'] = 10000 * r['links'] / r['eligible_articles']
        r['concentration'] = []
        years[key] = r
    for raw in read_csv('concentration'):
        r = numeric(raw, ('year', 'top_n', 'selected_firms', 'links'), ('link_share_pct',))
        key = (r['scope'], r['year'], r['period'])
        top = sorted(grouped_periods[key], key=lambda p: (-p['articles'], p['oib']))[:r['top_n']]
        assert len(top) == r['selected_firms'] and sum(p['articles'] for p in top) == r['links']
        assert math.isclose(r['link_share_pct'], 100 * r['links'] / years[key]['links'], abs_tol=1e-8)
        years[key]['concentration'].append({k: r[k] for k in ('top_n', 'selected_firms', 'links', 'link_share_pct')})

    publishers = defaultdict(set)
    publisher_links = Counter()
    all_publishers = defaultdict(set)
    for raw in read_csv('firm_publishers'):
        key = (raw['scope'], raw['oib'])
        assert raw['publisher'] not in publishers[key]
        publishers[key].add(raw['publisher'])
        publisher_links[key] += int(raw['articles'])
        all_publishers[raw['scope']].add(raw['publisher'])
    assert set(publishers) == set(persistence)
    assert all(publisher_links[k] == p['articles'] for k, p in persistence.items())

    overview = {'cohort_firms': len(firms), 'cohort_2023_members': sum(r['in2023'].lower() == 'true' for r in firms.values()),
                'membership_first_year': min(int(r['first_membership_year']) for r in firms.values()),
                'membership_last_year': max(int(r['last_membership_year']) for r in firms.values()),
                'first_month': months[0], 'last_month': months[-1], 'months': len(months),
                'common_publishers': len(list(read_csv('common_publishers')))}
    for scope in SCOPES:
        selected = [p for (s, _), p in persistence.items() if s == scope]
        overview[scope] = {'covered_firms': len(selected), 'links': sum(p['articles'] for p in selected),
                           'linked_publishers': len(all_publishers[scope]),
                           'eligible_articles': sum(m['documents'] for m in coverage[scope])}
        assert overview[scope]['links'] == sum(r['links'] for (s, y, period), r in years.items()
                                              if s == scope and (period == 'year' or y == 2026))
    overview.update(covered_firms=overview['media']['covered_firms'], article_firm_links=overview['media']['links'])

    hist = Counter(p['active_months'] for (s, _), p in persistence.items() if s == 'media')
    n = overview['media']['covered_firms']
    pers = {'scope': 'media', 'covered_firms': n,
            'histogram': [{'active_months': i, 'firms': hist[i]} for i in range(1, len(months) + 1)]}
    thresholds = {'one_month': lambda i: i == 1, 'at_most_three_months': lambda i: i <= 3,
                  'at_least_twelve_months': lambda i: i >= 12, 'at_least_thirty_six_months': lambda i: i >= 36,
                  'all_months': lambda i: i == len(months)}
    for key, predicate in thresholds.items():
        pers[key] = sum(count for active, count in hist.items() if predicate(active))
        pers[key + '_share_pct'] = 100 * pers[key] / n
    pers.update(le_three_months=pers['at_most_three_months'], le_three_months_pct=pers['at_most_three_months_share_pct'])
    bins = [(1, 1), (2, 3), (4, 11), (12, 35), (36, 66)]
    pers['bins'] = [{'min_months': low, 'max_months': high, 'firms': sum(hist[i] for i in range(low, high + 1))}
                    for low, high in bins]
    assert sum(p['firms'] for p in pers['bins']) == n
    pers['all_month_firms'] = [{'oib': oib, 'name': firms[oib]['display_name']} for (scope, oib), p in persistence.items()
                             if scope == 'media' and p['active_months'] == len(months)]

    def month_rows(oib, scope='media'):
        available = monthly.get((scope, oib), {})
        return [available.get(m, {'month': m, 'articles': 0, 'headline_articles': 0, 'outlets': 0}) for m in months]

    def full_period(oib, scope):
        p = persistence.get((scope, oib))
        if p is None:
            return {'articles': 0, 'active_months': 0, 'outlets': 0, 'peak_month_articles': 0,
                    'first_detected_month': None, 'last_detected_month': None}
        return {**{k: p[k] for k in ('articles', 'active_months', 'peak_month_articles', 'first_detected_month', 'last_detected_month')},
                'outlets': len(publishers[(scope, oib)])}

    def firm_h1(oib, scope, year):
        row = periods.get((scope, year, 'H1', oib))
        fields = ('articles', 'headline_articles', 'outlets', 'active_months', 'exact_text_groups')
        return {'year': year, 'period': 'H1', **({key: row[key] for key in fields} if row else {key: 0 for key in fields})}

    cases = {}
    for key, oib in CASES.items():
        assert oib in firms
        cases[key] = {'oib': oib, 'name': firms[oib]['display_name'], 'monthly': month_rows(oib),
                      'monthly_by_scope': {scope: month_rows(oib, scope) for scope in SCOPES},
                      'full_period': {scope: full_period(oib, scope) for scope in SCOPES},
                      'h1': {scope: {str(y): firm_h1(oib, scope, y) for y in (2025, 2026)} for scope in SCOPES}}
        cases[key].update(active_months=cases[key]['full_period']['media']['active_months'],
                          total_articles=cases[key]['full_period']['media']['articles'],
                          outlets=cases[key]['full_period']['media']['outlets'])
        cases[key]['h1'].update(cases[key]['h1']['media'])
    ranking = sorted(grouped_periods[('media', SELECTION_YEAR, 'year')], key=lambda p: (-p['articles'], p['oib']))
    top_rows = [{'rank_2023': rank, 'oib': r['oib'], 'name': firms[r['oib']]['display_name'],
                 'articles_2023': r['articles'], 'monthly': month_rows(r['oib']), 'full_period': full_period(r['oib'], 'media')}
                for rank, r in enumerate(ranking[:TOP_ROWS], 1)]
    rankings = {}
    for year, period in ((2021, 'year'), (2022, 'year'), (2023, 'year'), (2025, 'H1'), (2026, 'H1')):
        ordered = sorted(grouped_periods[('media', year, period)], key=lambda r: (-r['articles'], r['oib']))
        ranked = [{'rank': rank, 'oib': r['oib'], 'name': firms[r['oib']]['display_name'],
                   'articles': r['articles']} for rank, r in enumerate(ordered, 1)]
        rankings[f'{year}_{period}'] = {'year': year, 'period': period, 'top10': ranked[:10],
            'cases': {key: next((r for r in ranked if r['oib'] == oib), None) for key, oib in CASES.items()}}
    h1 = {}
    for scope in ('media', 'stable'):
        a, b = years[(scope, 2025, 'H1')], years[(scope, 2026, 'H1')]
        ca = next(c for c in a['concentration'] if c['top_n'] == 100)
        cb = next(c for c in b['concentration'] if c['top_n'] == 100)
        set_a = {r['oib'] for r in grouped_periods[(scope, 2025, 'H1')]}
        set_b = {r['oib'] for r in grouped_periods[(scope, 2026, 'H1')]}
        both, only_a, only_b = len(set_a & set_b), len(set_a - set_b), len(set_b - set_a)
        assert both + only_a == a['covered_firms'] and both + only_b == b['covered_firms']
        assert both + only_a + only_b == len(set_a | set_b)
        h1[scope] = {'2025': a, '2026': b,
                     'overlap': {'firms_both': both, 'only_2025': only_a, 'only_2026': only_b,
                                 'union': len(set_a | set_b), 'retained_2025_firms_pct': 100 * both / len(set_a),
                                 '2026_firms_also_in_2025_pct': 100 * both / len(set_b),
                                 'interpretation': 'Changes in detected links, not establishment, closure or a proof of entering/leaving actual media attention.'},
                     'change': {**{k + '_pct': change_pct(a[k], b[k]) for k in ('covered_firms', 'links', 'eligible_articles', 'links_per_10000_articles')},
                                'top100_share_percentage_points': cb['link_share_pct'] - ca['link_share_pct']}}
    annual = {scope: [years[(scope, year, 'H1' if year == 2026 else 'year')] for year in range(2021, 2027)] for scope in SCOPES}
    for name in INPUTS:
        assert (TABLES / f'{name}.csv').stat().st_mtime_ns == input_before[name], f'Input changed during extraction: {name}'
    output = {'created_utc': datetime.now(timezone.utc).isoformat(), 'overview': overview, 'persistence': pers,
              'annual_coverage': annual, 'coverage_monthly': coverage, 'h1_comparison': h1, 'cases': cases,
              'rankings': rankings,
              'top2023_rows': top_rows, 'selection': {'scope': 'media', 'ranking_year': SELECTION_YEAR, 'top_rows': TOP_ROWS,
                  'rule': 'Descending 2023 article–firm links, OIB tie-break; fixed firms across all 66 months. Named cases are illustrative additions.'},
              'interpretation': {'unit': 'accepted publisher-article–firm pair',
                  'scope': 'Current AEM-domain panel with saved page/pair/context exclusions; not an independently labelled journalism census.',
                  'zero': 'No detected accepted link in that month; not evidence of no coverage.',
                  'continuous_trend_supported': False,
                  'validation': 'No new human labels. Existing labels and source data were not changed.'},
              'checks': {'firm_month_to_persistence': True, 'firm_month_to_period': True, 'monthly_summary': True,
                         'yearly_summary': True, 'concentration': True, 'firm_publisher_totals': True, 'full_period_totals': True},
              'inputs': {str((TABLES / f'{name}.csv').relative_to(ROOT)): hashlib.sha256((TABLES / f'{name}.csv').read_bytes()).hexdigest()
                         for name in INPUTS}}
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'output': str(TARGET), 'overview': overview, 'persistence': {k: v for k, v in pers.items() if k not in ('histogram', 'bins')},
                      'h1_comparison': h1}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
