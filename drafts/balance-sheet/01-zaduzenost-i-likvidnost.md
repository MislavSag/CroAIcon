# Visoka poluga, plitka likvidnost -> Firme s puno duga i malo gotovine pune predstecaj, stecaj i likvidaciju

*Biljeska za buduci post. Sve konkretne brojke su za provjeru, nisu nas nalaz. Tema ceka ciscenje financijskih stupaca GFI baze.*

[Otvaranje. Opener orijentira. Zaduzenost je najprisutnija tema o financijama na razini firme, a FINA panel veze dug i likvidnost na kasniji ishod (predstecaj, stecaj, likvidacija). Bridge poziva. Pogledajmo koje firme padaju, i je li smrtonosna kombinacija ona koju ocekujemo. [stub: povezi s podnaslovom gore i s prvom brojkom dolje].]

## Visoka poluga i niska likvidnost zajedno ubijaju

[Caption grafa. Udio firmi po kvadrantu poluga x likvidnost, i stopa kasnijeg steceva po kvadrantu.]

[Stub proze. Brojka bi vodila. [ocekujemo da firme u kvadrantu visoka poluga + niska likvidnost imaju visestruko vecu stopu kasnijeg steceva od ostalih]. Ni poluga sama ni plitka likvidnost sama nisu presuda. Tek zajedno. [stub: precizan omjer i grube magnitude tek nakon ciscenja stupaca].]

[KUT] Je li smrtonosna kombinacija visoka poluga i plitka likvidnost, ili jedan omjer nosi vecinu signala.

## Pokrice kamata odvaja preziveloga od posrnuloga

[Caption grafa. Distribucija pokrica kamata (EBIT / troskovi kamata) za firme koje su prezivjele i one koje su kasnije pale.]

[Stub proze. [ocekujemo da firme s pokricem kamata ispod 1 nose najvecu stopu kasnijeg ishoda], jer firma koja ne pokriva ni kamatu zivi na rok. Neto dug i D/E daju sliku tereta, pokrice kamata daje sliku daha. [stub: prag i udio firmi ispod njega tek nakon ciscenja].]

[KUT] Koji omjer prvi pukne. Bilancni (D/E, neto dug) ili tokovni (pokrice kamata).

## Profil rizika dijeli dobitnike od gubitnika

[Samo ako tema nudi pobjednike i gubitnike. Ovdje su to firme po profilu rizika, ne djelatnosti.]

Dobitnici. [Firme s niskom polugom i zdravom tekucom likvidnoscu. [ocekujemo nisku stopu kasnijeg steceva].]

Gubitnici. [Firme s visokom polugom i tekucom likvidnoscu ispod 1. [ocekujemo da ovaj profil dominira u predstecaju, stecaju i likvidaciji].]

[KUT - glavna interpretacija] Koliko rano FINA panel vidi pad. Ako poluga i likvidnost predvidaju ishod godinama unaprijed, omjeri su rani alarm, a ne tek obdukcija.

[Payoff. Stub za so-what. [Ako se profil rizika cita iz bilance prije pada, pitanje nije tko je pao, nego zasto je signal stajao neprocitan. Tek nakon ciscenja stupaca mozemo reci koliko rano i koliko pouzdano.]]

## Napomene

- Izvor. FINA, Godisnji financijski izvjestaji (db_afs). Dopunski, za usporedbu modela. Altman Z-score literatura.
- Tablica. `db_afs`
- Stupci / omjeri. Dug i kapital (D/E), kratkotrajna imovina i kratkorocne obveze (tekuca likvidnost), neto dug, EBIT i troskovi kamata (pokrice kamata). Veza na kasniji ishod (predstecaj, stecaj, likvidacija) kroz panel.
- Oprez. Svi navedeni omjeri traze financijske stupce GFI baze, koji jos nisu procisceni (mapiranje bNNN na FINA AOP je nepouzdano). Do potvrde stupaca tema ostaje hipoteza, ne nalaz. Gdje tema dira broj firmi, siri obuhvat baze nije rast.

---

## Biljeske za izradu

- Nalaz (ocekivani). Firme koje spajaju visoku polugu i nisku likvidnost imale bi visestruko vecu stopu kasnijeg steceva od firmi sa zdravom bilancom. Pokrice kamata ispod 1 bilo bi najjaci pojedinacni signal. Grube magnitude tek nakon ciscenja stupaca.
- Podaci. Tablica `db_afs`. Omjeri D/E, tekuca likvidnost, neto dug, pokrice kamata, plus veza na ishod kroz panel. Status povjerenja. SVI omjeri traze financijske stupce -> danas NEPOUZDANO (bNNN != FINA AOP). Metadata stupci (`employeecounteop`, `nacerev21`) ostaju jedini pouzdani, ali sami ne nose ovu temu.
- Kut. Je li smrtonosna kombinacija (poluga + likvidnost) ili jedan omjer, i koliko rano panel vidi pad.
- Vanjske brojke za provjeru (NE u tijelu kao nas nalaz).
  - 82% firmi s prihodom > 5 mil. EUR u financijskim teskocama imalo visoku ili vrlo visoku zaduzenost. Izvor. Lider / istrazivanje. Za provjeru.
  - 95% takvih firmi imalo slabu ili vrlo slabu likvidnost. Izvor. Lider / istrazivanje. Za provjeru.
  - 17 od 18 takvih firmi zavrsilo u predstecaju, stecaju ili likvidaciji. Izvor. Lider / istrazivanje. Za provjeru.
- Mediji / izvori. Mediji. Lider, Poslovni.hr, Jutarnji list. Institucije. FINA, HNB.
- Tezina. Velika. Trazi cisto mapiranje financijskih stupaca i konstrukciju panela na ishod.
- Verdikt. Park - ceka ciscenje financijskih stupaca GFI baze.
