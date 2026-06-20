# AI.econ

**Stranica uživo:** <https://MislavSag.github.io/CroAIcon>

AI.econ je Quarto analitički blog za hrvatske gospodarske podatke, GFI izvještaje i Eurostat serije. Projekt je pripremljen za rad u Positronu, uz R kao glavni analitički jezik i Python za AI nacrte tekstova.

## Brzi start

```powershell
cd C:\Users\Mislav\projects_r\CroAIcon
Rscript scripts/update_data.R
quarto preview
```

Quarto preview koristi port `4200`, ako je slobodan.

## R paketi

Projekt radi bez automatskog `renv` aktiviranja. Za instalaciju paketa u standardnu R biblioteku:

```powershell
Rscript scripts/setup_r_packages.R
```

Ako želiš koristiti projektni `renv`, pokreni:

```powershell
$env:CROAICON_USE_RENV = "true"
Rscript scripts/setup_r_packages.R
```

`arrow` i `duckdb` mogu trajati dulje pri prvoj instalaciji, osobito na Windowsima.

## Otvaranje u Positronu

Otvori folder `C:\Users\Mislav\projects_r\CroAIcon` ili datoteku `CroAIcon.Rproj`.

## Struktura

```text
posts/      Quarto blog postovi
R/          R funkcije za podatke, grafove, tablice i warehouse
python/     AI nacrti i pomoćne provjere
data/       Lokalni sirovi i obrađeni podaci, ignorirano u Gitu
outputs/    Generirane činjenice, tablice i grafovi
prompts/    Upute za AI generiranje nacrta
scripts/    Operativne skripte
```

## Data workflow

1. Sirovi GFI podaci idu u `data/raw/gfi/` ili u folder naveden kroz `GFI_SOURCE_DIR`.
2. Eurostat i GFI skripte pripremaju podatke u `data/processed/`.
3. Analitičke tablice mogu se spremiti u `data/warehouse/croaicon.duckdb`.
4. Provjerene brojke za AI nacrt idu u `outputs/facts/*.json`.
5. AI nacrt ide u `drafts/ai/`, a nakon provjere se ručno prebacuje u `posts/`.

## AI nacrt

Bez API poziva:

```powershell
python python/ai_draft.py --facts outputs/facts/example_facts.json --offline
```

S OpenAI API-jem:

1. Kopiraj `env.example` u `.env`.
2. Postavi `OPENAI_API_KEY` i `OPENAI_MODEL`.
3. Pokreni:

```powershell
python python/ai_draft.py --facts outputs/facts/example_facts.json
```

Skripta koristi OpenAI Responses API kada su dostupni ključ, model i paket `openai`. Ako nešto nedostaje, napravi offline strukturirani nacrt.

## Novi post

```powershell
Rscript scripts/new_post.R "Naslov nove analize"
```

## Komentari

Komentari su pripremljeni kroz Giscus u `_quarto.yml`.

```yaml
MislavSag/CroAIcon
```

Repo mora biti javan i mora imati uključene GitHub Discussions. U Giscusu odaberi kategoriju `Announcements` ili prilagodi kategoriju u `_quarto.yml`.

## GitHub Pages

Workflow je u `.github/workflows/publish.yml`. Za objavu:

1. Napravi javni GitHub repo `CroAIcon`.
2. Pushaj `main` ili `master` branch.
3. U GitHub repo postavkama uključi Pages preko GitHub Actions.

Ako GFI podaci nisu javni, ne stavljaj ih u repo. Render može ostati lokalni, a javno se objavljuje samo HTML rezultat.
