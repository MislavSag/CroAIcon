# Objavljivanje posta Turizam bez nazivnika

## Opseg objave

- `posts/2026-07-turizam-bez-nazivnika/`
- `_freeze/posts/2026-07-turizam-bez-nazivnika/`
- `data/external/tourism_external.csv`
- `python/tourism_value_build.py`
- `MEMORY.md`
- pripadajući planovi i završni QA izvještaj za ovaj post

Ne uključivati stariju verziju posta `posts/2026-07-noc-bez-cijene/`, njezin freeze,
ostale planove, istraživanja ni generirane `site_libs`.

## Priprema

1. Ukloniti samo literalne `[KUT]` oznake. Zadržati sav odobreni tekst.
2. Postaviti `draft: false`.
3. Pokrenuti `qa-post` nad objavnom verzijom. Potrebno je najmanje 90 bodova.
4. Ponovno pokrenuti analitički i grafički pipeline.
5. Renderirati post i cijelu stranicu te vizualno pregledati objavnu verziju.

## GitHub

1. Otvoriti granu `agent/publish-turizam-bez-nazivnika`.
2. Stageati samo datoteke iz opsega objave.
3. Commitati, pushati i otvoriti PR prema `main`.
4. Provjeriti GitHub Actions i status objave. Ne uključivati nepovezane promjene iz
   radnog stabla.
