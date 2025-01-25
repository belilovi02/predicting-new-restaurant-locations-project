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
    "Sarajevo": [(43.8486, 18.3564), (43.8480, 18.3600), (43.8500, 18.3530)],  # Samo prijmer, zamijeni sa stvarnim podacima
    "Mostar": [(43.3441, 17.8074), (43.3450, 17.8095)],
    "Banja Luka": [(44.7719, 17.1923), (44.7730, 17.1935)],
    "Zenica": [(44.2001, 17.9104), (44.2020, 17.9125)],
    "Tuzla": [(44.5344, 18.6750), (44.5350, 18.6758)],
    "Bihać": [(44.8140, 15.8687), (44.8155, 15.8692)],
    "Trebinje": [(42.7084, 18.3437), (42.7090, 18.3450)],
    "Doboj": [(44.7769, 18.1103), (44.7778, 18.1120)],
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
