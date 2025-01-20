from flask import Flask, request, jsonify, render_template
import pandas as pd
from sklearn.cluster import KMeans
import geopandas as gpd
from shapely.geometry import Point

app = Flask(__name__)

# Učitaj podatke o naseljenim područjima (GeoJSON format)
settlement_data = gpd.read_file("geoBoundaries-BIH-ADM0_simplified.geojson")

# Endpoint za unos i analizu podataka
@app.route("/process", methods=["POST"])
def process_data():
    # Primanje podataka iz zahtjeva
    data = request.json
    print("Primljeni podaci:", data)  # Ispis dolaznih podataka

    if not data or 'locations' not in data:
        return jsonify({"error": "Nedostaju podaci"}), 400

    locations = data['locations']
    num_clusters = data.get('numClusters', 3)
    print("Broj klastera:", num_clusters)

    if len(locations) < num_clusters:
            return jsonify({"error": "Premalo lokacija za traženi broj klastera"}), 400

    df = pd.DataFrame(locations, columns=["latitude", "longitude"])
    print("DataFrame kreiran:", df)

    # Pretvori u GeoDataFrame
    points = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
    geo_df = gpd.GeoDataFrame(df, geometry=points, crs="EPSG:4326")

    # Prostorno spajanje s naseljenim područjima
    geo_df = gpd.sjoin(geo_df, settlement_data, predicate="intersects")

    # Provjera da li postoje podaci
    if geo_df.empty:
        return jsonify({"error": "Nema validnih lokacija unutar naseljenih područja."}), 400

    # K-means clustering s provjerom da nema duplikata
    # num_clusters = 3
    max_attempts = 10  # Ograničenje broja pokušaja kako bi se izbjegla beskonačna petlja
    attempt = 0
    unique_centroids = False

    while not unique_centroids and attempt < max_attempts:
        kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
        geo_df['cluster'] = kmeans.fit_predict(geo_df[['latitude', 'longitude']])
        centroids = kmeans.cluster_centers_

        # Provjera da li su centroids različiti od početnih tačaka
        centroid_tuples = set(tuple(row) for row in centroids)
        input_tuples = set(tuple(xy) for xy in zip(df['latitude'], df['longitude']))

        if centroid_tuples.isdisjoint(input_tuples):
            unique_centroids = True  # Svi centroidi su različiti
        else:
            attempt += 1  # Pokušaj ponovo

    if not unique_centroids:
        return jsonify({"error": "Nije moguće generisati različite klastere nakon više pokušaja."}), 400

    # Vraćanje predloženih lokacija
    result = [{"latitude": lat, "longitude": lon} for lat, lon in centroids]

    return jsonify(result)

# Početna stranica sa mapom
@app.route("/")
def index():
    return render_template("map.html")
    
if __name__ == "__main__":
    app.run(debug=True)
