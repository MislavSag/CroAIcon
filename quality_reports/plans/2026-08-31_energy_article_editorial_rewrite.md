# Energetika. Uredničko prepisivanje

Status: završeno 31. kolovoza 2026.

1. Preusmjeriti članak s tehničke priče o korpusu na jednu javnu priču. Šok 2022. brzo mijenja pažnju, dok se fizička struktura i tržišna moć mijenjaju sporije.
2. Zamijeniti naslov, podnaslov, uvod i završetak. Otvoriti računom za struju i solarnim panelom. Zatvoriti vezom između pažnje, instalirane tehnologije i računa kućanstva.
3. Ukloniti vidljive reference na proširenje korpusa, arhive, puni tekst, feedove, prekide i tehničke provjere. Zadržati kratak i pošten okvir izvora u `## Napomene`.
4. Prvi grafikon ograničiti na neprekinuto razdoblje 2021. do 2023. Ne spajati razine preko stvarne promjene izvora. Pojednostaviti naslove i izvore ostalih grafikona.
5. Ponovno pokrenuti skriptu grafikona, provjeriti četiri PNG-a, renderirati Quarto objavu i pregledati završni HTML. Ažurirati QA zapis samo činjenicama iz novog rendera.

Ishod. Tekst i grafikoni prepisani, sve provjere u `energy_validation.csv` prolaze, četiri PNG-a ponovno izrađena i pregledana, a Quarto render uspješno zapisan u `_site/`. U završnom HTML-u nema `[KUT]` markera ni vidljivih tehničkih digresija o medijskom prikupljanju. Pregled cijele stranice u pregledniku nije bio dostupan u sesiji; struktura HTML-a i sva četiri grafikona provjereni su zasebno. Skripte su prije objave preimenovane u `energy_attention_balance_*`.
