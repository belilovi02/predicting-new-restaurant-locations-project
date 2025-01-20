Aplikacija **"Restoran Lokator"** omogućuje korisnicima interaktivno mapiranje i analizu geografskih podataka s ciljem identificiranja optimalnih lokacija za nove restorane. Funkcionalnosti su implementirane kroz backend servis u Pythonu (koristeći Flask) i frontend temeljen na HTML-u, CSS-u i Leaflet.js biblioteci za prikaz mape.

### Kako aplikacija funkcionira:
1. **Unos lokacija:**
   - Korisnici mogu desnim klikom na mapu dodavati geografske točke koje predstavljaju postojeće ili planirane lokacije restorana.
   - Svaka unesena lokacija automatski se prikazuje u tablici, gdje korisnici mogu pregledati geografske koordinate i ukloniti neželjene točke.

2. **Analiza podataka:**
   - Kada korisnik klikne na gumb **"Predloži lokacije"**, aplikacija šalje sve unesene točke zajedno s brojem željenih klastera na backend servis.
   - Backend koristi **K-means algoritam** za klasterizaciju unesene liste lokacija, grupirajući točke u zadani broj klastera (npr. 3 klastera za 3 optimalne lokacije).
   - Sustav provjerava valjanost lokacija i osigurava da predloženi centri klastera (centroidi) budu jedinstveni i prostorno različiti od početnih točaka.
   - Prije izračuna klastera, aplikacija koristi prostornu obradu s **GeoPandas** i **Shapely** bibliotekama kako bi osigurala da se unesene lokacije nalaze unutar naseljenih područja Bosne i Hercegovine, definiranih u GeoJSON datoteci.

3. **Prikaz rezultata:**
   - Predložene lokacije klastera (centroidi) vraćaju se na frontend i prikazuju na mapi pomoću crvenih markera, dok su korisnički unosi prikazani plavim markerima.
   - Korisnik može vizualno pregledati kako su predložene lokacije povezane s postojećim podacima.

4. **Reset funkcionalnost:**
   - Gumb **"Resetiraj lokacije"** omogućuje korisnicima uklanjanje svih dodanih markera i rezultata s mape te resetiranje aplikacije na početno stanje.

### Tehnološki detalji:
- **Backend:** Flask API prihvaća JSON podatke i obrađuje ih koristeći:
  - **GeoPandas** za prostornu analizu i spajanje podataka s geografskim područjima.
  - **Shapely** za kreiranje geometrijskih objekata.
  - **Scikit-learn** za implementaciju K-means algoritma.
- **Frontend:** 
  - **Leaflet.js** omogućuje prikaz OpenStreetMap mape i interakciju s korisnicima (dodavanje markera, prikaz rezultata).
  - **HTML i CSS** koriste se za strukturiranje i stiliziranje sadržaja, uključujući tablicu unosa i legendu za označavanje markera.
- **Prostorni podaci:** Aplikacija koristi GeoJSON datoteku s podacima o naseljenim područjima Bosne i Hercegovine kako bi se osigurala relevantnost prijedloga.

### Svrha:
Aplikacija je namijenjena vlasnicima restorana, planerima ili analitičarima koji žele odrediti gdje bi novi restorani bili najpogodniji, temeljem prostornog rasporeda postojećih lokacija. Pomoću klasterizacije i geografskih podataka pruža korisnicima mogućnost donošenja informiranih odluka o pozicioniranju objekata.