/* Static publication checks: exact 150-firm selection, monthly values and links. */
const fs=require('fs'),path=require('path'),assert=require('assert');
const root=process.argv[2]||'posts/2026-09-firme-u-medijima/atlas';
const facts=JSON.parse(fs.readFileSync('outputs/facts/gfi_media_atlas_public.json','utf8'));
const filenames=['index.html',...Array.from({length:4},(_,i)=>'stranica-'+(i+2)+'.html')];
const read=p=>fs.readFileSync(p,'utf8');
const decode=s=>s.replaceAll('&amp;','&').replaceAll('&lt;','<').replaceAll('&gt;','>').replaceAll('&quot;','"').replaceAll('&#x27;',"'");
assert.equal(facts.firms.length,150);
const allRows=[];
for(let page=0;page<5;page++){
  const html=read(path.join(root,filenames[page]));
  assert(!/<(?:script|input|select|button|dialog|iframe|form)\b/i.test(html));
  assert(!/\bon(?:click|change|input|load)\s*=/i.test(html));
  assert(!/\b(?:OIB|Determ)\b|Potraži|Klikni|interaktiv|nedostaj|nepotpun/i.test(html));
  const tbody=html.match(/<tbody>([\s\S]*?)<\/tbody>/)[1];
  assert(!/<a\b/.test(tbody));
  const rows=[...tbody.matchAll(/<tr>([\s\S]*?)<\/tr>/g)];
  assert.equal(rows.length,30);
  rows.forEach((match,i)=>{
    const expected=facts.firms[page*30+i],row=match[1];
    const rank=Number(row.match(/class="rank">(\d+)\./)[1]);assert.equal(rank,expected.rank);
    const name=decode(row.match(/<\/span> ([\s\S]*?)<\/th>/)[1]);assert.equal(name,expected.name);
    const cells=[...row.matchAll(/<td[^>]*>([\d.]+)<\/td>/g)].map(m=>Number(m[1].replaceAll('.','')));
    assert.deepEqual(cells,[...expected.monthly_articles,expected.total_articles]);
    allRows.push({rank,name});
  });
  const navs=[...html.matchAll(/<nav\b[^>]*>([\s\S]*?)<\/nav>/g)];assert.equal(navs.length,2);
  for(const nav of navs){assert.equal([...nav[1].matchAll(/<a\b/g)].length,4);assert(nav[1].includes('aria-current="page">'+(page+1)));}
  for(const match of html.matchAll(/href="([^"]+)"/g)){
    if(/^https:/.test(match[1]))continue;
    const target=path.resolve(root,match[1]);
    assert(fs.existsSync(target)||(match[1]==='../index.html'&&fs.existsSync(target.replace(/\.html$/,'.qmd'))),match[1]);
  }
}
assert.deepEqual(allRows.map(r=>r.rank),Array.from({length:150},(_,i)=>i+1));
assert.equal(fs.readdirSync(root).filter(f=>f.endsWith('.html')).length,5);
console.log(JSON.stringify({passed:true,pages:5,firms:150,monthly_values_checked:2700,totals_checked:150,
  page_navigation_verified:true,no_javascript_controls_identifiers_or_article_links:true},null,2));
