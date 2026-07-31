# Turizam bez nazivnika. Druga verzija posta

## Cilj

Napraviti zasebnu verziju posta `Noć bez cijene` koja ne mijenja postojeći nacrt. Nova
verzija vodi jednom tezom: hrvatska turistička statistika ima zajednički broj noćenja,
ali nema javno usporediv prihod za dva različita modela smještaja. Podjela na
poduzeća i kućanstva objašnjava zašto nazivnik nedostaje.

## Urednička odluka

- Glavni kut: *turizam bez nazivnika*.
- Objašnjenje: pod jednim turističkim rezultatom djeluju dva različita gospodarska
  modela, poduzeća i kućanstva.
- Ne tvrditi da prihod kućanstava ne postoji ili da ga država ne može vidjeti.
  Tvrdnja je uža: objavljeni podaci ne daju usporediv prihod po noćenju za kućanstva
  i poduzeća.
- Broj od 40 eura ostaje mjera prolaska prihoda kroz društva, nikada cijena.
- Broj od 176 eura ostaje ukupna potrošnja stranog gosta po stranoj noći, nikada
  cijena smještaja.

## Opseg

1. Izraditi `posts/2026-07-turizam-bez-nazivnika/index.qmd`.
2. Zadržati svih deset postojećih grafikona i analitičke nalaze.
3. Presložiti tekst tako da kućanstva i problem usporedivosti dolaze odmah nakon
   prve mjere od 40 eura.
4. Svaku kasniju analizu povezati s glavnom tezom. Županije pokazuju posljedicu
   različite strukture, marine pokazuju što dobivamo kada se novac i količina mogu
   spojiti, a stabilan udio hotela pokazuje da je riječ o trajnom modelu.
5. Ukloniti stare `[KUT]` oznake jer je autor u ovom koraku izabrao kut.
6. Ne uvoditi novu analizu ni nove brojke.

## Provjera

- Ponovno pokrenuti `python/tourism_value_build.py`.
- Provjeriti da prolaze sve stavke u `outputs/tables/tourism_validation.csv`.
- Ponovno pokrenuti `python/tourism_value_charts.py`.
- Renderirati novu verziju uz projektni Python.
- Provjeriti broj grafikona, numeričko podebljanje, izostanak dugih crtica,
  odsutnost `[KUT]` oznaka i čitljivost završnog HTML-a.
