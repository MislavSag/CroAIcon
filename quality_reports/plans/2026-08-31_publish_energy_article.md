# Objavljivanje energetskog članka

Status: završeno 31. kolovoza 2026.

1. Popisati sve datoteke potrebne za članak i potvrditi da su unutar CroAIcon repozitorija. Izvorni i izvedeni podatkovni skupovi ostaju izvan commita.
2. Postaviti `draft: false`, obnoviti grafikone i Quarto freeze zapis te renderirati cijeli site.
3. Provjeriti da objava ulazi u naslovnicu, pretragu i RSS te da GitHub Actions može renderirati članak bez lokalnih podataka.
4. Stageati samo datoteke energetskog članka, njegove skripte, slike, freeze, QA, plan i autorsku korekciju u `MEMORY.md`. Ne uključiti postojeće nevezane izmjene.
5. Commitati, sigurno prenijeti commit na produkcijsku granu i pushati na GitHub. Potvrditi rezultat udaljenog pusha i, ako je dostupno, stanje deploy workflowa.

Ishod. U commit ulaze članak, četiri PNG-a, dvije prijenosne skripte, Quarto freeze, QA i urednički zapisi. Izvorni korpus, EIZ PDF, GFI baza i generirani `outputs/` ostaju izvan commita. Puni `quarto render` prolazi u čistoj radnoj kopiji s `origin/main` bez lokalnih energetskih podataka. Objava ulazi u naslovnicu, pretragu i RSS.
