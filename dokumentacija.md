Ovaj projekat omogućava razvoj aplikacije koja koristi geografske podatke 
kako bi prikazala lokacije restorana u Bosni i Hercegovini, kao i predložene 
lokacije za nove restorane, zasnovane na analizama podataka o trenutnoj raspodjeli restorana. 
Aplikacija koristi TomTom API za pretragu podataka o restoranima u određenoj regiji i K-means algoritam 
za grupisanje restorana i predlaganje novih lokacija.

Detaljan opis:
1. Frontend - HTML & JavaScript (Leaflet.js):
HTML Struktura: Na početnoj stranici nalazi se jednostavan form s dva unosa
 (latitude i longitude) koja omogućavaju korisniku da unese geografske koordinate. 
 Korisnik može unijeti tačne koordinate bilo koje lokacije u Bosni i Hercegovini 
 i nakon toga pritisnuti dugme "Prikazi Restorane" kako bi pokrenuo pretragu.
Map: Mapa je prikazana putem Leaflet.js biblioteke, koja omogućava interaktivne 
mape na webu. Mapu pokreće osnovni sloj sa OpenStreetMap tileovima.
Responzivni Dizajn: Kroz CSS je implementiran responzivni dizajn koji 
omogućava da stranica bude funkcionalna i na mobilnim uređajima, 
smanjujući veličinu elemenata kada se stranica prikazuje na manjim ekranima.

2. Backend - Python (Flask & TomTom API):
Flask Web Framework: Flask je korišćen za kreiranje servera koji preuzima podatke od korisnika, 
koristi TomTom API da dobije podatke o restoranima u određenom radijusu, 
obrađuje te podatke i vraća ih u formatu koji frontend može prikazati na mapi.
TomTom API: API omogućava pretragu restorana i drugih objekata na osnovu geografske širine i dužine. 
Aplikacija koristi endpoint za pretragu objekata u određenom radijusu od unesene tačke. 
Kada korisnik unese koordinate, API poziva se za pretragu restorana.
K-means Algoritam: Koristi se za grupisanje restorana na mapi. 
Algoritam analizira trenutne lokacije restorana i predlaže nove lokacije (centroids) 
na osnovu gustoće postojećih restorana. Ove lokacije označene su crvenim kružnicama na mapi, 
što predstavlja potencijalna područja za nove restorane.
3. Podaci i Prikazivanje na Mapi:
Restorani: Nakon što API vrati listu restorana, svaki restoran je označen na mapi sa markerom. 
Kada korisnik klikne na marker, pojavljuje se popup koji prikazuje ime restorana.
Potencijalne Lokacije (Centroids): Na osnovu analize podataka o postojećim restoranima, K-means 
algoritam generiše predložene lokacije za nove restorane (centroids). Svaka od tih lokacija je 
prikazana kao crveni krug na mapi, što korisnicima omogućava vizualizaciju potencijalnih mjesta za novi restoran.
4. Interaktivnost:
Korisnici mogu učitati mapu na osnovu različitih geografskih koordinata koje unesu, 
a mape se automatski ažuriraju sa novim podacima nakon svakog poziva API-ja.
Ovaj interaktivni pristup omogućava korisnicima da istraže različite regije u Bosni i Hercegovini 
i da dobiju vizualne prijedloge za nove restorane temeljem podataka iz trenutnih restoranskih lokacija.
Zaključak:
Projekat predstavlja dinamičan i interaktivan sistem za praćenje i analizu restoranske industrije 
u Bosni i Hercegovini. Kombinovanjem geografske analize pomoću TomTom API-ja i machine learning tehnike K-means, 
omogućava se korisnicima da ne samo istraže trenutne restorane, već i da dobiju preporuke za nove lokacije. 
Pored toga, aplikacija je dizajnirana s obzirom na mobilne uređaje, što čini ovu funkcionalnost dostupnom na svim platformama.

Sistem može biti koristan za različite poslovne analize, kao što su:

Planiranje novih restorana bazirano na analizi gustine postojećih restorana.
Poboljšanje tržišne strategije pomoću geografske analize lokacija.
Optimizacija poslovanja u industriji ugostiteljstva.
Aplikacija takođe omogućava proširivanje na različite regione, omogućavajući korisnicima da biraju različite lokacije za analize, čime se omogućava šira primjena i skalabilnost sistema.