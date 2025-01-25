from flask import Flask, request, jsonify, render_template
import pandas as pd
from sklearn.cluster import KMeans
import geopandas as gpd
from shapely.geometry import Point
from sklearn.preprocessing import StandardScaler
from sklearn.utils.extmath import row_norms
import requests
import time
import random
from sklearn.metrics import pairwise_distances_argmin_min
import numpy as np
from sklearn.cluster import DBSCAN

app = Flask(__name__)

# Definicija gradova i njihovih restorana
cities = {
    "Sarajevo": [
        (43.8486, 18.3564), (43.8480, 18.3600), (43.8500, 18.3530),
        (43.8560, 18.3660), (43.8520, 18.3620), (43.8470, 18.3500),
        (43.8490, 18.3580), (43.8550, 18.3590), (43.8515, 18.3550),
        (43.8535, 18.3575), (43.8540, 18.3540), (43.8450, 18.3525),
        (43.8445, 18.3610), (43.8465, 18.3635), (43.8475, 18.3680),
        (43.8485, 18.3655), (43.8495, 18.3640), (43.8505, 18.3615),
        (43.8570, 18.3680), (43.8430, 18.3500), (43.8600, 18.3700),
        (43.8425, 18.3650), (43.8615, 18.3580), (43.8580, 18.3555),
        (43.8415, 18.3510), (43.8620, 18.3575), (43.8590, 18.3595),
        (43.8565, 18.3645), (43.8455, 18.3480), (43.8440, 18.3475),
        (43.8460, 18.3705), (43.8470, 18.3720), (43.8480, 18.3740),
        (43.8490, 18.3760), (43.8500, 18.3780), (43.8510, 18.3800),
        (43.8520, 18.3820), (43.8530, 18.3840), (43.8540, 18.3860),
        (43.8550, 18.3880), (43.8560, 18.3900)
    ],
    "Mostar": [
        (43.3441, 17.8074), (43.3450, 17.8095), (43.3460, 17.8105),
        (43.3470, 17.8115), (43.3480, 17.8125), (43.3490, 17.8135),
        (43.3500, 17.8145), (43.3510, 17.8155), (43.3520, 17.8165),
        (43.3530, 17.8175), (43.3540, 17.8185), (43.3550, 17.8195),
        (43.3560, 17.8205), (43.3570, 17.8215), (43.3580, 17.8225),
        (43.3590, 17.8235), (43.3600, 17.8245), (43.3610, 17.8255),
        (43.3620, 17.8265), (43.3630, 17.8275), (43.3640, 17.8285),
        (43.3650, 17.8295), (43.3660, 17.8305), (43.3670, 17.8315),
        (43.3680, 17.8325), (43.3690, 17.8335), (43.3700, 17.8345),
        (43.3710, 17.8355), (43.3720, 17.8365)
    ],
    "Banja Luka": [
        (44.7719, 17.1923), (44.7730, 17.1935), (44.7740, 17.1945),
        (44.7750, 17.1955), (44.7760, 17.1965), (44.7770, 17.1975),
        (44.7780, 17.1985), (44.7790, 17.1995), (44.7800, 17.2005),
        (44.7810, 17.2015), (44.7820, 17.2025), (44.7830, 17.2035),
        (44.7840, 17.2045), (44.7850, 17.2055), (44.7860, 17.2065),
        (44.7870, 17.2075), (44.7880, 17.2085), (44.7890, 17.2095),
        (44.7900, 17.2105), (44.7910, 17.2115), (44.7920, 17.2125),
        (44.7930, 17.2135), (44.7940, 17.2145), (44.7950, 17.2155),
        (44.7960, 17.2165), (44.7970, 17.2175), (44.7980, 17.2185),
        (44.7990, 17.2195), (44.8000, 17.2205)
    ],
    "Zenica": [
        (44.2001, 17.9104), (44.2020, 17.9125), (44.2040, 17.9145),
        (44.2060, 17.9165), (44.2080, 17.9185), (44.2100, 17.9205),
        (44.2120, 17.9225), (44.2140, 17.9245), (44.2160, 17.9265),
        (44.2180, 17.9285), (44.2200, 17.9305), (44.2220, 17.9325),
        (44.2240, 17.9345), (44.2260, 17.9365), (44.2280, 17.9385),
        (44.2300, 17.9405), (44.2320, 17.9425), (44.2340, 17.9445),
        (44.2360, 17.9465), (44.2380, 17.9485), (44.2400, 17.9505),
        (44.2420, 17.9525), (44.2440, 17.9545), (44.2460, 17.9565),
        (44.2480, 17.9585), (44.2500, 17.9605), (44.2520, 17.9625),
        (44.2540, 17.9645), (44.2560, 17.9665)
    ],
    "Tuzla": [
        (44.5344, 18.6750), (44.5350, 18.6758), (44.5360, 18.6765),
        (44.5370, 18.6775), (44.5380, 18.6785), (44.5390, 18.6795),
        (44.5400, 18.6805), (44.5410, 18.6815), (44.5420, 18.6825),
        (44.5430, 18.6835), (44.5440, 18.6845), (44.5450, 18.6855),
        (44.5460, 18.6865), (44.5470, 18.6875), (44.5480, 18.6885),
        (44.5490, 18.6895), (44.5500, 18.6905), (44.5510, 18.6915),
        (44.5520, 18.6925), (44.5530, 18.6935), (44.5540, 18.6945),
        (44.5550, 18.6955), (44.5560, 18.6965), (44.5570, 18.6975),
        (44.5580, 18.6985), (44.5590, 18.6995), (44.5600, 18.7005),
        (44.5610, 18.7015), (44.5620, 18.7025)
    ],
    "Bihać": [
        (44.8140, 15.8687), (44.8155, 15.8692), (44.8160, 15.8700),
        (44.8170, 15.8710), (44.8180, 15.8720), (44.8190, 15.8730),
        (44.8200, 15.8740), (44.8210, 15.8750), (44.8220, 15.8760),
        (44.8230, 15.8770), (44.8240, 15.8780), (44.8250, 15.8790),
        (44.8260, 15.8800), (44.8270, 15.8810), (44.8280, 15.8820),
        (44.8290, 15.8830), (44.8300, 15.8840), (44.8310, 15.8850),
        (44.8320, 15.8860), (44.8330, 15.8870), (44.8340, 15.8880),
        (44.8350, 15.8890), (44.8360, 15.8900), (44.8370, 15.8910),
        (44.8380, 15.8920), (44.8390, 15.8930), (44.8400, 15.8940),
        (44.8410, 15.8950), (44.8420, 15.8960)
    ],
    "Trebinje": [
        (42.7084, 18.3437), (42.7090, 18.3450), (42.7100, 18.3460),
        (42.7110, 18.3470), (42.7120, 18.3480), (42.7130, 18.3490),
        (42.7140, 18.3500), (42.7150, 18.3510), (42.7160, 18.3520),
        (42.7170, 18.3530), (42.7180, 18.3540), (42.7190, 18.3550),
        (42.7200, 18.3560), (42.7210, 18.3570), (42.7220, 18.3580),
        (42.7230, 18.3590), (42.7240, 18.3600), (42.7250, 18.3610),
        (42.7260, 18.3620), (42.7270, 18.3630), (42.7280, 18.3640),
        (42.7290, 18.3650), (42.7300, 18.3660), (42.7310, 18.3670),
        (42.7320, 18.3680), (42.7330, 18.3690), (42.7340, 18.3700),
        (42.7350, 18.3710), (42.7360, 18.3720)
    ],
    "Doboj": [
        (44.7769, 18.1103), (44.7778, 18.1120), (44.7780, 18.1130),
        (44.7790, 18.1140), (44.7800, 18.1150), (44.7810, 18.1160),
        (44.7820, 18.1170), (44.7830, 18.1180)],
}

settlement_data = gpd.read_file("geoBoundaries-BIH-ADM0_simplified.geojson")

# Funkcija za pretragu restorana u gradu
def get_restaurants_for_city(city_name):
    if city_name in cities:
        return cities[city_name]
    else:
        return []


# Nova funkcija za generisanje slučajnih početnih centara
def random_centroid_initialization(data, n_clusters):
    """
    Funkcija za slučajnu inicijalizaciju centara klastera.
    """
    random_indices = random.sample(range(len(data)), n_clusters)
    initial_centroids = data[random_indices]
    return initial_centroids

# DBSCAN klasterisanje (I način)
@app.route("/process_dbscan", methods=["POST"])
def process_data_dbscan():
    data = request.json
    print("Primljeni podaci:", data)

    if not data or 'locations' not in data:
        return jsonify({"error": "Nedostaju podaci"}), 400

    locations = data['locations']

    if len(locations) < 3:
        return jsonify({"error": "Minimalno 3 lokacije potrebne za predikciju"}), 400

    # Pretvoriti ulazne podatke u DataFrame
    df = pd.DataFrame(locations, columns=["latitude", "longitude"])
    points = df[['latitude', 'longitude']].values

    db = DBSCAN(eps=0.01, min_samples=3).fit(points)
    df['cluster'] = db.labels_

    # Prikupljanje predloženih lokacija
    proposed_locations = []
    for cluster_label in set(df['cluster']):
        cluster_points = df[df['cluster'] == cluster_label]
        # Prosečna tačka svakog klastera
        cluster_center = cluster_points[['latitude', 'longitude']].mean()
        proposed_locations.append({
            "latitude": cluster_center['latitude'],
            "longitude": cluster_center['longitude'],
            "population_density": "Nepoznato"
        })

    return jsonify(proposed_locations)

# (II način)
@app.route("/process_random", methods=["POST"])
def process_data_random():
    data = request.json
    print("Primljeni podaci:", data)

    if not data or 'locations' not in data:
        return jsonify({"error": "Nedostaju podaci"}), 400

    locations = data['locations']
    num_clusters = data.get('numClusters', 3)
    print("Broj klastera:", num_clusters)

    if len(locations) < num_clusters:
        return jsonify({"error": "Premalo lokacija za traženi broj klastera"}), 400

    # Pretvoriti ulazne podatke u DataFrame
    df = pd.DataFrame(locations, columns=["latitude", "longitude"])
    points = df[['latitude', 'longitude']].values

    # Normalizacija podataka
    scaler = StandardScaler()
    normalized_points = scaler.fit_transform(points)

    # Nasumična inicijalizacija centara klastera
    initial_centroids = random_centroid_initialization(normalized_points, num_clusters)

    # Kreiraj klastere pomoću KMeans-a s random inicijalizacijom
    kmeans = KMeans(n_clusters=num_clusters, init=initial_centroids, n_init=1, random_state=None)
    df['cluster'] = kmeans.fit_predict(normalized_points)
    centroids = kmeans.cluster_centers_

    # Transformacija centara nazad u originalne koordinate
    centroids = scaler.inverse_transform(centroids)

    proposed_locations = []
    for lat, lon in centroids:
        try:
            response = requests.get(
                f"https://nominatim.openstreetmap.org/reverse",
                params={
                    "lat": lat,
                    "lon": lon,
                    "format": "json",
                    "addressdetails": 1
                },
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                city = data.get("address", {}).get("city", "Nepoznato")
                proposed_locations.append({
                    "latitude": lat,
                    "longitude": lon,
                    "city": city
                })
            else:
                proposed_locations.append({
                    "latitude": lat,
                    "longitude": lon,
                    "city": "Nepoznato"
                })
        except requests.exceptions.Timeout:
            proposed_locations.append({
                "latitude": lat,
                "longitude": lon,
                "city": "Nepoznato (timeout)"
            })
        except requests.exceptions.RequestException as e:
            proposed_locations.append({
                "latitude": lat,
                "longitude": lon,
                "city": f"Greška: {str(e)}"
            })

    return jsonify(proposed_locations)

# Endpoint za analizu podataka (KMeans) - III način
@app.route("/process", methods=["POST"])
def process_data():
    data = request.json
    print("Primljeni podaci:", data)

    if not data or 'locations' not in data:
        return jsonify({"error": "Nedostaju podaci"}), 400

    locations = data['locations']
    num_clusters = data.get('numClusters', 3)
    print("Broj klastera:", num_clusters)

    if len(locations) < num_clusters:
        return jsonify({"error": "Premalo lokacija za traženi broj klastera"}), 400

    df = pd.DataFrame(locations, columns=["latitude", "longitude"])
    print("DataFrame kreiran:", df)

    points = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
    geo_df = gpd.GeoDataFrame(df, geometry=points, crs="EPSG:4326")

    # Prostorno spajanje s naseljenim područjima
    geo_df = gpd.sjoin(geo_df, settlement_data, predicate="intersects")

    if geo_df.empty:
        return jsonify({"error": "Nema validnih lokacija unutar naseljenih područja."}), 400

    # Dodavanje težinskih faktora (simulirana gustoća populacije)
    def get_population_density(lat, lon):
        try:
            response = requests.get(
                "https://nominatim.openstreetmap.org/reverse",
                params={
                    "lat": lat,
                    "lon": lon,
                    "format": "json",
                    "addressdetails": 1
                },
                timeout=5
            )
            
            # Provjera statusa odgovora
            if response.status_code == 200:
                data = response.json()
                # Povlačenje gustoće naseljenosti (ako postoji)
                return data.get("address", {}).get("population_density", 1)
            else:
                print(f"Greška: API vratio status {response.status_code}")
                return 1  # Default vrijednost ako nema odgovora
        except requests.exceptions.Timeout:
            print("Timeout prilikom poziva API-ja.")
            return 1  # Default vrijednost za timeout
        except requests.exceptions.RequestException as e:
            print(f"Greška prilikom poziva API-ja: {e}")
            return 1  # Default vrijednost za ostale greške
        except ValueError as e:
            print(f"Greška prilikom parsiranja JSON-a: {e}")
            return 1  # Default vrijednost za greške pri parsiranju

    # Primjena funkcije na DataFrame
    geo_df['population_density'] = geo_df.apply(
        lambda row: (time.sleep(1), get_population_density(row['latitude'], row['longitude']))[1],
        axis=1
    )

    # Normalizacija podataka
    scaler = StandardScaler()
    geo_df[['latitude', 'longitude']] = scaler.fit_transform(geo_df[['latitude', 'longitude']])
    weights = geo_df['population_density'].values

    max_attempts = 5
    attempt = 0
    unique_centroids = False

    while not unique_centroids and attempt < max_attempts:
        # Težinski prilagođeni KMeans
        kmeans = KMeans(n_clusters=num_clusters, init="random", random_state=None, n_init=10, max_iter=300)
        geo_df['cluster'] = kmeans.fit_predict(geo_df[['latitude', 'longitude']], sample_weight=weights)
        centroids = kmeans.cluster_centers_

        # Transformacija nazad u geografske koordinate
        centroids = scaler.inverse_transform(centroids)

        centroid_tuples = set(tuple(row) for row in centroids)
        input_tuples = set(tuple(xy) for xy in zip(df['latitude'], df['longitude']))

        if centroid_tuples.isdisjoint(input_tuples):
            unique_centroids = True
        else:
            attempt += 1

    if not unique_centroids:
        return jsonify({"error": "Nije moguće generisati različite klastere nakon više pokušaja."}), 400

    proposed_locations = []
    for lat, lon in centroids:
        try:
            response = requests.get(
                f"https://nominatim.openstreetmap.org/reverse",
                params={
                    "lat": lat,
                    "lon": lon,
                    "format": "json",
                    "addressdetails": 1
                },
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                population_density = data.get("address", {}).get("city", "Nepoznato")
                proposed_locations.append({
                    "latitude": lat,
                    "longitude": lon,
                    "population_density": population_density
                })
            else:
                proposed_locations.append({
                    "latitude": lat,
                    "longitude": lon,
                    "population_density": "Nepoznato"
                })
        except requests.exceptions.Timeout:
            # Ako dođe do timeouta, dodaj default vrijednosti
            proposed_locations.append({
                "latitude": lat,
                "longitude": lon,
                "population_density": "Nepoznato (timeout)"
            })
        except requests.exceptions.RequestException as e:
            # Ostale greške u zahtjevu
            proposed_locations.append({
                "latitude": lat,
                "longitude": lon,
                "population_density": f"Greška: {str(e)}"
            })

    return jsonify(proposed_locations)


@app.route("/search_restaurants", methods=["GET"])
def search_restaurants():
    city_name = request.args.get('city_name', '')
    if not city_name:
        return jsonify({"error": "Nema unesenog naziva grada"}), 400

    # Pretraži restorane u tom gradu
    restaurants = get_restaurants_for_city(city_name)
    locations = []
    
    for restaurant in restaurants:
        locations.append({
            "latitude": restaurant[0],
            "longitude": restaurant[1]
        })

    # Predložene nove lokacije pomoću KMeans algoritma
    return jsonify({"restaurants": locations})

# Početna stranica sa mapom
@app.route("/")
def index():
    return render_template("map.html")

if __name__ == "__main__":
    app.run(debug=True)
