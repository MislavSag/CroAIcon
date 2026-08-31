# QA. Od računa za struju do solara na krovu

**Status. Uredničko prepisivanje je završeno. Post je objavljen s `draft: false` i nema otvorenih uredničkih markera.**

## Urednički rezultat

- Novi naslov i podnaslov ne koriste okvir mita i stvarnosti.
- Uvod spaja račun za struju, LNG i solarni panel. Zaključak vraća isti motiv kroz vezu između pažnje, instalirane tehnologije i računa kućanstva.
- Tekst ne spominje proširenje korpusa, promjene arhiva, dostupnost punog teksta ni feedove.
- Završni odjeljak povezuje tri razine analize. Medijska pažnja mijenja se brzo, fizička struktura sporije, a prihod pokazuje koncentriranu sposobnost ulaganja.
- Nema `[KUT]` markera.

## Brojevi i grafikoni

- Svih sedam spremljenih provjera u `outputs/tables/energy_validation.csv` prolazi.
- Inline vrijednosti čitaju se iz `outputs/facts/energy_attention_balance.json` i `outputs/tables/energy_media_topic_shift.csv`.
- `python/energy_attention_balance_charts.py` ponovno je pokrenut nakon uredničke izmjene.
- Sva četiri PNG-a ponovno su izrađena u `outputs/figures/` i kopirana u mapu posta. Pojedinačno su pregledani i čitljivi na širini članka.
- Prvi grafikon prikazuje jednu neprekinutu vremensku liniju od 2021. do 2023. bez tehničkih oznaka o prikupljanju podataka.

## Render

- Quarto je uspješno renderirao post u `_site/posts/2026-08-energetika-izmedu-naslova-i-bilance/index.html`.
- Završni HTML sadrži novi naslov, svih pet odjeljaka i reference na sva četiri grafikona.
- Pretraga HTML-a ne nalazi `[KUT]` ni uklonjene tehničke izraze.
- Puni site render prolazi u čistoj radnoj kopiji temeljenoj na `origin/main`, bez lokalnih energetskih tablica i facts datoteke. GitHub Actions zato može koristiti spremljeni Quarto freeze bez pristupa izvornim podacima.
- Objava je prisutna na naslovnici, u `search.json` i u RSS-u `index.xml`.
- Izvorni korpus, EIZ PDF, GFI baza i generirani `outputs/` nisu dio commita.
- Preglednik za lokalni cjelostranični prikaz nije bio povezan u ovoj sesiji. Provjera je zato obuhvatila uspješan render, strukturu HTML-a i zaseban vizualni pregled sva četiri grafikona.
