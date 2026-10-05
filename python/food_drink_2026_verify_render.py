"""Check the rendered article, then make a simple Markdown reading copy."""
import hashlib
import json
import argparse
from pathlib import Path
import re
from lxml import html

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / 'drafts/food-drink-2026/article.qmd'
POST = ROOT / 'posts/2026-10-hrana-pice-iza-naslova/index.qmd'
HTML = ROOT / '_site/posts/2026-10-hrana-pice-iza-naslova/index.html'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--site-dir', type=Path, default=ROOT / '_site')
    parser.add_argument('--published', action='store_true')
    args = parser.parse_args()
    site_dir = args.site_dir.resolve()
    page_path = site_dir / 'posts/2026-10-hrana-pice-iza-naslova/index.html'
    source = DRAFT.read_text(encoding='utf-8')
    facts = json.loads((ROOT / 'outputs/facts/food_drink_2026.json').read_text(encoding='utf-8'))
    tree = html.fromstring(page_path.read_bytes())
    main_node = tree.xpath('//main')[0]
    text = ' '.join(main_node.text_content().split())
    assert POST.read_bytes() == DRAFT.read_bytes(), 'Post copy is stale'
    assert 'author: []' in source
    assert ('draft: false' if args.published else 'draft: true') in source
    kut_count = len(re.findall(r'\[KUT\]', source))
    assert kut_count <= 3
    if args.published:assert kut_count == 0
    assert text.count('[KUT]') == kut_count and 'Napomene' in text
    assert '{python}' not in text and 'Traceback' not in text
    assert not tree.xpath('//meta[@name="author"]'), 'Unexpected inherited author'
    expected = []
    def substitute(match):
        expression = re.fullmatch(r'n\("([^"]+)"(?:, (\d+))?\)(\.lstrip\("-"\))?', match[1])
        assert expression, match[1]
        key, digits, strip_minus = expression.groups()
        value = f'{facts[key]:,.{int(digits or 0)}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
        if strip_minus:
            value = value.lstrip('-')
        expected.append(value)
        return value
    resolved = re.sub(r'(?<!`)`\{python\}[^\S\r\n]*([^`\r\n]+)`', substitute, source)
    for value in expected:
        assert value in text, f'Expected rendered value absent: {value}'
    pictures = main_node.xpath('.//img')
    assert len(pictures) == 3, len(pictures)
    for img in pictures:
        asset = (page_path.parent / img.get('src')).resolve()
        assert asset.is_file(), asset
        canonical = ROOT / 'outputs/figures/food_drink_2026' / asset.name
        assert canonical.read_bytes() == asset.read_bytes(), f'Stale figure: {asset}'
        assert img.get('alt'), 'Figure needs alternative text'
    subtitle = re.search(r'^subtitle: "(.+)"$', source, re.M)[1]
    title = re.search(r'^title: "(.+)"$', source, re.M)[1]
    assert subtitle in text and title in text
    ids = set(tree.xpath('//@id'))
    toc_links = tree.xpath('//nav[@id="TOC"]//a[starts-with(@href,"#")]/@href')
    assert toc_links and all(link[1:] in ids for link in toc_links)
    assert tree.xpath('//button[@data-bs-toggle="collapse"]'), 'Navbar menu control absent'
    for button in tree.xpath('//button[@data-bs-target]'):
        target = button.get('data-bs-target')
        if target.startswith('#'):assert target[1:] in ids, target
    assert tree.xpath('//*[@id="quarto-search"]'), 'Search control absent'
    if args.published:
        slug = 'posts/2026-10-hrana-pice-iza-naslova/'
        for filename in ('index.html','search.json','index.xml'):
            assert slug in (site_dir / filename).read_text(encoding='utf-8'), f'Post absent from {filename}'
        assert 'Nacrt' not in main_node.text_content()
    body = re.sub(r'\A---.*?---\s*', '', resolved, count=1, flags=re.S)
    body = re.sub(r'```\{python\}.*?```\s*', '', body, flags=re.S)
    body = re.sub(r'\)\{fig-alt="[^"]*"\}', ')', body)
    body = re.sub(r'\((0[123]_[^)]+\.png)\)', r'(../../posts/2026-10-hrana-pice-iza-naslova/\1)', body)
    preview = ROOT / 'drafts/food-drink-2026/article-preview.md'
    preview.write_text(f'# {title}\n\n*{subtitle}*\n\n' + body, encoding='utf-8')
    report = dict(
        render_passed=True, canonical_post_matches=True, figures=3,
        inline_numeric_expressions_checked=len(expected), kut_markers=kut_count,
        inherited_author=False, browser_visual_check=False,
        browser_limitation='CUA returned no available browsers; charts inspected as images.',
        html_sha256=hashlib.sha256(page_path.read_bytes()).hexdigest(),
        draft_sha256=hashlib.sha256(DRAFT.read_bytes()).hexdigest(),
        published=args.published, site_dir=str(site_dir), toc_links=len(toc_links),
        navigation_targets_valid=True, homepage_search_feed_verified=args.published,
        analysis_status='Preliminary; development sample reviewed, no independent recall or precision estimate.',
    )
    (ROOT / 'quality_reports/2026-10-05_food-drink-render-verification.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
