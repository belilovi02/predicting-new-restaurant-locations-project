from flask import Flask, request, jsonify, render_template
import pandas as pd
from sklearn.cluster import KMeans
import geopandas as gpd
from shapely.geometry import Point
import requests

app = Flask(__name__)

# Definicija gradova i njihovih restorana
cities = {
    "Sarajevo": [(43.8486, 18.3564), (43.8480, 18.3600), (43.8500, 18.3530)],  # Samo primer, zameni sa stvarnim podacima
    "Mostar": [(43.3441, 17.8074), (43.3450, 17.8095)],
    "Banja Luka": [(44.7719, 17.1923), (44.7730, 17.1935)],
    "Zenica": [(44.2001, 17.9104), (44.2020, 17.9125)],
    "Tuzla": [(44.5344, 18.6750), (44.5350, 18.6758)],
    "Bihać": [(44.8140, 15.8687), (44.8155, 15.8692)],
    "Trebinje": [(42.7084, 18.3437), (42.7090, 18.3450)],
    "Doboj": [(44.7769, 18.1103), (44.7778, 18.1120)],
}

# Funkcija za pretragu restorana u gradu
def get_restaurants_for_city(city_name):
    if city_name in cities:
        return cities[city_name]
    else:
        return []

# Endpoint za analizu podataka (KMeans)
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

    max_attempts = 10
    attempt = 0
    unique_centroids = False

    while not unique_centroids and attempt < max_attempts:
        kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
        geo_df['cluster'] = kmeans.fit_predict(geo_df[['latitude', 'longitude']])
        centroids = kmeans.cluster_centers_

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
        response = requests.get(f"https://nominatim.openstreetmap.org/reverse", params={
            "lat": lat,
            "lon": lon,
            "format": "json",
            "addressdetails": 1
        })
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
    num_clusters = 3  # Možete podesiti broj klastera prema potrebi
    return jsonify({"restaurants": locations, "num_clusters": num_clusters})

# Početna stranica sa mapom
@app.route("/")
def index():
    return render_template("map.html")

if __name__ == "__main__":
    app.run(debug=True)
