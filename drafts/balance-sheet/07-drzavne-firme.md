# Gubitak je proračunska stavka -> Velike državne firme godinama režu operativne gubitke koje pokriva proračun, a teret se gomila izvan bilance

*Bilješka za budući post. Sve konkretne brojke su za provjeru, nisu naš nalaz, i žive samo u bloku Vanjske brojke za provjeru. Tema čeka čišćenje financijskih stupaca GFI baze.*

Državne firme su pod stalnim povećalom (javna nabava, upravljački promašaji, gubici). Pogledajmo ih kao portfelj, ne kao niz pojedinačnih skandala. [Obećanje. Koliko velikih državnih firmi godinama posluje s operativnim gubitkom, koliko taj gubitak pokriva proračun, i koliki se teret skuplja tamo gdje bilanca ne gleda.]

## Operativni gubitak nije iznimka, nego stalna stavka

[Caption grafa. Operativni rezultat najvećih državnih firmi po godini, sivo. firme s gubitkom.]

[Stub proze. Brojka bi vodila. Koliki udio velikih državnih firmi reže operativni gubitak više godina zaredom, i koliki je kumulativni preneseni gubitak na razini portfelja. [Očekujemo da operativni gubitak nije jednokratni šok nego ponavljana stavka kod jezgre portfelja, s prenesenim gubitkom koji raste iz godine u godinu.]]

[KUT] Razlika između firme koja je imala lošu godinu i firme čiji je gubitak postao poslovni model.

## Dokapitalizacija je samo drugo ime za zatvaranje proračunske rupe

[Caption grafa. Kapitalni transferi i dokapitalizacije u državne firme po godini.]

[Stub proze. Brojka bi vodila. Koliko je kapitala ubrizgano u firme koje operativno ne pokrivaju troškove, i kako se injekcije u kapital poklapaju s godinama najvećih operativnih gubitaka. [Očekujemo da dokapitalizacije prate gubitke s odmakom, tako da transfer u kapital zapravo zatvara operativnu rupu, a ne financira ulaganje.]]

[KUT] Kada dokapitalizacija prestaje biti ulaganje i postaje tihi transfer iz proračuna.

## Dobitnici stoje na vlastitom prihodu, gubitnici žive na transferima

[Dobitnici. [Firme koje uredno pokrivaju troškove iz prihoda, bez transfera, i koje teret ne guraju izvan bilance. Imenovati ih iz portfelja kad brojke budu čvrste.]]

[Gubitnici. [Jezgra portfelja koja godinama živi na transferima, sa starim obvezama prema dobavljačima i dugom pod državnim jamstvom. Imenovati kad brojke budu čvrste.]]

[KUT - glavna interpretacija] Fiskalni rizik se ne vidi u proračunskom saldu nego u portfelju. Izvanbilančne kontingentne obveze, starost obveza prema dobavljačima i dug s državnim jamstvom su odgođeni račun. [Središnja interpretacija. Što portfelj govori o tome gdje se rizik stvarno skuplja i tko ga na kraju plaća.]

[Payoff. Stub za so-what. Ne sažetak nego što ostaje kad se gubici, transferi i jamstva poslože u jednu sliku. [Npr. da pravo pitanje nije koliko je jedna firma izgubila ove godine, nego koliko je proračuna tiho rezervirano za portfelj koji operativno ne stoji.]]

## Napomene

- Izvor. FINA, Godišnji financijski izvještaji (`db_afs`) + Sudski registar (vlasništvo) + HNB makro podaci (fiskalni rizik).
- Tablica. `db_afs`
- Stupci / omjeri. Operativni rezultat i kumulativni preneseni gubitak. Kapitalni transferi i dokapitalizacije (injekcije u kapital). Izvanbilančne kontingentne obveze. Starost obveza prema dobavljačima. Dug s državnim jamstvom. Vlasništvo (državna povezanost) iz Sudskog registra.
- Oprez. Financijski stupci GFI baze još nisu pročišćeni (mapiranje `bNNN` nije pouzdano jednako FINA AOP), pa nijedan financijski omjer ovdje nije izračunat. Gdje tema dira broj firmi, širi obuhvat baze nije stvarni rast. Definicija državne povezanosti (udio, izravno ili neizravno) mora se fiksirati prije izračuna.

---

## Bilješke za izradu

- Nalaz (očekivani). Jezgra velikih državnih firmi bi godinama trebala generirati operativni gubitak pokriven kapitalnim transferima, uz preneseni gubitak i izvanbilančni teret (jamstva, stare obveze) koji bi rastao i kad operativni rezultat povremeno poskoči.
- Podaci. `db_afs` + Sudski registar (vlasništvo) + HNB (fiskalni rizik). Omjeri. Operativni gubitak i kumulativni preneseni gubitak, dokapitalizacije i kapitalni transferi, izvanbilančne kontingentne obveze, starost obveza prema dobavljačima, dug s državnim jamstvom. Status povjerenja. SVI traže financijske stupce -> danas NEPOUZDANO.
- Kut. Gubitak kao proračunska stavka, a ne kao incident. Fiskalni rizik živi u portfelju, ne u godišnjem saldu.
- Vanjske brojke za provjeru. (Medijske, NISU naš nalaz, za provjeru.) 2013. do 2020. državno povezane firme dobile su otprilike pola vrijednosti ugovora javne nabave (Nacional, Index.hr). HRT, HŽ Infrastruktura i Hrvatske ceste navode se kao firme čiji su operativni gubici apsorbirani državnim transferima (Jutarnji list). Sve treba reproducirati iz primarnih izvora prije ulaska u tijelo.
- Mediji / izvori. Mediji. Nacional, Index.hr, Jutarnji list. Institucije / izvori. FINA, Ministarstvo, Sudski registar, HNB.
- Težina. Velika.
- Verdikt. Park - čeka čišćenje financijskih stupaca GFI baze.
